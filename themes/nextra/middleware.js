import { locales } from 'nextra/locales';
import { NextResponse } from 'next/server';

export function middleware(request) {
  const { nextUrl } = request;

  // 🛡️ 静态资源与数据文件绝对放行（防 Nextra 多语言路由劫持导致 404）
  if (
    nextUrl.pathname.startsWith('/_next') ||
    nextUrl.pathname.startsWith('/api') ||
    nextUrl.pathname.endsWith('.json') ||
    nextUrl.pathname.endsWith('.js') ||
    nextUrl.pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // 🛡️ [多语言根路由防劫持自愈]
  // 当创作者从控制台一键直达预览站点 (?t=...) 或直接请求根路径时：
  // 若无显式语言前缀，清除/忽略历史残留的 NEXT_LOCALE Cookie，确保 100% 默认展示原稿主语言
  if (nextUrl.pathname === '/' || nextUrl.pathname === '') {
    if (request.cookies.has('NEXT_LOCALE') && (nextUrl.searchParams.has('t') || nextUrl.searchParams.has('locale'))) {
      request.cookies.delete('NEXT_LOCALE');
      const res = locales(request) || NextResponse.next();
      res.cookies.delete('NEXT_LOCALE');
      return res;
    }
  }

  return locales(request);
}
