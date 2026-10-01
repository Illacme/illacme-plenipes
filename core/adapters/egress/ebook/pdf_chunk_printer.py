# -*- coding: utf-8 -*-
"""
Illacme Plenipes - PDF Chunked Printer & Instant Merger
模块职责：针对长篇典籍与多语双开面对照长卷，执行分块/分批无头打印并瞬时合并。
根治痛点：根除 Chromium Blink 引擎在单一大 HTML (100+ 页复杂断页) 上的指数级重排死锁与 300s+ 假死超时。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import tempfile
import subprocess
from typing import List
from core.utils.tracing import tlog


class PDFChunkPrinter:
    """🖨️ PDF 分块打印与 PyMuPDF 瞬时合并引擎"""

    DEFAULT_CHUNK_SIZE = 64

    @classmethod
    def render_and_merge(
        cls,
        chrome_bin: str,
        head_html: str,
        sections: List[str],
        tail_html: str,
        out_pdf: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> bool:
        """分批渲染 HTML 片段并合并输出最终 PDF"""
        if not sections:
            return False

        # 1. 章节较少或单篇时，执行零开销单 HTML 极速直出
        if len(sections) <= chunk_size:
            full_html = head_html + "\n".join(sections) + tail_html
            return cls._print_single_html(chrome_bin, full_html, out_pdf)

        # 2. 长卷多节切片
        chunks = [sections[i:i + chunk_size] for i in range(0, len(sections), chunk_size)]
        tlog.info(f"📚 [PDF分块打印] 启动长卷分块流水线: 共 {len(sections)} 个节, 切分为 {len(chunks)} 个分卷批次")

        temp_pdfs: List[str] = []
        try:
            for idx, chunk in enumerate(chunks, 1):
                chunk_html = head_html + "\n".join(chunk) + tail_html
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tf:
                    tf.write(chunk_html)
                    tmp_h = tf.name

                tmp_p = tmp_h.replace(".html", ".pdf")
                try:
                    success = cls._print_single_html(chrome_bin, chunk_html, tmp_p, timeout=45)
                    if not success or not os.path.exists(tmp_p):
                        tlog.warning(f"⚠️ [PDF分块打印] 分卷 {idx}/{len(chunks)} 渲染未就绪")
                        return False
                    temp_pdfs.append(tmp_p)
                finally:
                    if os.path.exists(tmp_h):
                        try:
                            os.remove(tmp_h)
                        except Exception:
                            pass

            # 3. 毫秒级原生高保真合并所有分卷
            return cls._merge_pdfs(temp_pdfs, out_pdf)

        except Exception as e:
            tlog.error(f"❌ [PDF分块打印] 分卷合并流水线异常: {e}")
            return False
        finally:
            for p in temp_pdfs:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    @classmethod
    def _print_single_html(cls, chrome_bin: str, html_content: str, out_pdf: str, timeout: int = 60) -> bool:
        """调用无头 Chrome 打印单个 HTML"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tf:
            tf.write(html_content)
            tmp_html = tf.name

        try:
            file_url = f"file://{tmp_html}"
            cmd = [
                chrome_bin, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-first-run",
                "--disable-background-networking", "--disable-default-apps", "--disable-extensions", "--disable-sync",
                "--disable-translate", "--disable-features=OptimizationHints,OptimizationGuideModelDownloading",
                f"--print-to-pdf={out_pdf}", file_url
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            if result.stderr and b'Printing failed' in result.stderr:
                tlog.warning(f"⚠️ [PDF单分卷打印] 渲染器报错: {result.stderr.decode('utf-8', errors='replace')[:200]}")
                return False
            return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 200
        except Exception as e:
            tlog.warning(f"⚠️ [PDF单分卷打印] 调用异常: {e}")
            return False
        finally:
            if os.path.exists(tmp_html):
                try:
                    os.remove(tmp_html)
                except Exception:
                    pass

    @classmethod
    def _merge_pdfs(cls, pdf_paths: List[str], out_pdf: str) -> bool:
        """基于 PyMuPDF (fitz) 或 PyPDF2 毫秒级拼接多卷 PDF"""
        if not pdf_paths:
            return False

        # 优先使用 C 级极速 PyMuPDF (优先标准 pymupdf 杜绝废弃警告，兼容旧版 fitz)
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open()
            for p in pdf_paths:
                sub_doc = fitz.open(p)
                doc.insert_pdf(sub_doc)
                sub_doc.close()
            doc.save(out_pdf)
            doc.close()
            tlog.info(f"✨ [PDF分块打印] PyMuPDF 极速拼接完成: {len(pdf_paths)} 卷已落盘 -> {out_pdf}")
            return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 200
        except ImportError:
            pass
        except Exception as fe:
            tlog.warning(f"⚠️ [PDF分块打印] PyMuPDF 拼接降级: {fe}")

        # 备选 1: 现代纯 Python 工业标准 pypdf (零编译依赖，全平台通用)
        try:
            from pypdf import PdfWriter
            writer = PdfWriter()
            for p in pdf_paths:
                writer.append(p)
            with open(out_pdf, "wb") as f_out:
                writer.write(f_out)
            writer.close()
            tlog.info(f"✨ [PDF分块打印] pypdf 现代标准拼接完成: {len(pdf_paths)} 卷已落盘 -> {out_pdf}")
            return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 200
        except ImportError:
            pass
        except Exception as pye:
            tlog.warning(f"⚠️ [PDF分块打印] pypdf 拼接降级: {pye}")

        # 备选 2: 遗留 PyPDF2
        try:
            import PyPDF2
            merger = PyPDF2.PdfMerger()
            for p in pdf_paths:
                merger.append(p)
            merger.write(out_pdf)
            merger.close()
            tlog.info(f"✨ [PDF分块打印] PyPDF2 备选拼接完成 -> {out_pdf}")
            return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 200
        except Exception as pe:
            tlog.error(f"❌ [PDF分块打印] 所有 PDF 合并器均不可用: {pe}")
            return False
