/**
 * Illacme Plenipes - Vault Bindery QR Vector Engine
 * 模块职责：纯客户端零依赖超轻量 QR 码矢量 SVG 渲染核心（支持 Version 1~10，纠错级别 M）。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */
(function() {
    'use strict';

    const QRMode = { MODE_8BIT_BYTE: 4 };
    const QRMaskPattern = { PATTERN000: 0, PATTERN001: 1, PATTERN010: 2, PATTERN011: 3, PATTERN100: 4, PATTERN101: 5, PATTERN110: 6, PATTERN111: 7 };
    const QRUtil = {
        PATTERN_POSITION_TABLE: [[], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50], [6, 30, 54]],
        G15: (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | 1,
        G15_MASK: (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1),
        getBCHTypeInfo: function(data) {
            let d = data << 10;
            while (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15) >= 0) d ^= (QRUtil.G15 << (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15)));
            return ((data << 10) | d) ^ QRUtil.G15_MASK;
        },
        getBCHDigit: function(data) {
            let digit = 0;
            while (data != 0) { digit++; data >>>= 1; }
            return digit;
        },
        getMask: function(maskPattern, i, j) {
            switch (maskPattern) {
                case QRMaskPattern.PATTERN000: return (i + j) % 2 == 0;
                case QRMaskPattern.PATTERN001: return i % 2 == 0;
                case QRMaskPattern.PATTERN010: return j % 3 == 0;
                case QRMaskPattern.PATTERN011: return (i + j) % 3 == 0;
                case QRMaskPattern.PATTERN100: return (Math.floor(i / 2) + Math.floor(j / 3)) % 2 == 0;
                case QRMaskPattern.PATTERN101: return (i * j) % 2 + (i * j) % 3 == 0;
                case QRMaskPattern.PATTERN110: return ((i * j) % 2 + (i * j) % 3) % 2 == 0;
                case QRMaskPattern.PATTERN111: return ((i * j) % 3 + (i + j) % 2) == 0;
                default: throw new Error('bad maskPattern:' + maskPattern);
            }
        },
        getErrorCorrectPolynomial: function(errorCorrectLength) {
            let a = new QRPolynomial([1], 0);
            for (let i = 0; i < errorCorrectLength; i++) a = a.multiply(new QRPolynomial([1, QRMath.gexp(i)], 0));
            return a;
        }
    };

    const QRMath = {
        glog: function(n) { if (n < 1) throw new Error('glog(' + n + ')'); return QRMath.LOG_TABLE[n]; },
        gexp: function(n) { while (n < 0) n += 255; while (n >= 255) n -= 255; return QRMath.EXP_TABLE[n]; },
        EXP_TABLE: new Array(256), LOG_TABLE: new Array(256)
    };
    for (let i = 0; i < 8; i++) QRMath.EXP_TABLE[i] = 1 << i;
    for (let i = 8; i < 256; i++) QRMath.EXP_TABLE[i] = QRMath.EXP_TABLE[i - 4] ^ QRMath.EXP_TABLE[i - 5] ^ QRMath.EXP_TABLE[i - 6] ^ QRMath.EXP_TABLE[i - 8];
    for (let i = 0; i < 255; i++) QRMath.LOG_TABLE[QRMath.EXP_TABLE[i]] = i;

    function QRPolynomial(num, shift) {
        let offset = 0;
        while (offset < num.length && num[offset] == 0) offset++;
        this.num = new Array(num.length - offset + shift);
        for (let i = 0; i < num.length - offset; i++) this.num[i] = num[i + offset];
    }
    QRPolynomial.prototype = {
        get: function(index) { return this.num[index]; },
        getLength: function() { return this.num.length; },
        multiply: function(e) {
            const num = new Array(this.getLength() + e.getLength() - 1);
            for (let i = 0; i < this.getLength(); i++) {
                for (let j = 0; j < e.getLength(); j++) num[i + j] ^= QRMath.gexp(QRMath.glog(this.get(i)) + QRMath.glog(e.get(j)));
            }
            return new QRPolynomial(num, 0);
        },
        mod: function(e) {
            if (this.getLength() - e.getLength() < 0) return this;
            const ratio = QRMath.glog(this.get(0)) - QRMath.glog(e.get(0));
            const num = new Array(this.getLength());
            for (let i = 0; i < this.getLength(); i++) num[i] = this.get(i);
            for (let i = 0; i < e.getLength(); i++) num[i] ^= QRMath.gexp(QRMath.glog(e.get(i)) + ratio);
            return new QRPolynomial(num, 0).mod(e);
        }
    };

    const RS_BLOCK_TABLE = [
        [], [1, 26, 16], [1, 44, 28], [1, 70, 44], [2, 50, 32], [2, 67, 43],
        [4, 43, 27], [4, 49, 31], [4, 60, 38], [4, 70, 44], [4, 80, 50]
    ];

    function QRBitBuffer() { this.buffer = []; this.length = 0; }
    QRBitBuffer.prototype = {
        put: function(num, length) { for (let i = 0; i < length; i++) this.putBit(((num >>> (length - i - 1)) & 1) == 1); },
        putBit: function(bit) {
            const bufIndex = Math.floor(this.length / 8);
            if (this.buffer.length <= bufIndex) this.buffer.push(0);
            if (bit) this.buffer[bufIndex] |= (0x80 >>> (this.length % 8));
            this.length++;
        }
    };

    function QRCodeModel(typeNumber) {
        this.typeNumber = typeNumber;
        this.modules = null;
        this.moduleCount = 0;
        this.dataList = [];
    }
    QRCodeModel.prototype = {
        addData: function(data) {
            const bytes = [];
            for (let i = 0; i < data.length; i++) {
                const c = data.charCodeAt(i);
                if (c < 128) bytes.push(c);
                else if (c < 2048) { bytes.push((c >> 6) | 192); bytes.push((c & 63) | 128); }
                else { bytes.push((c >> 12) | 224); bytes.push(((c >> 6) & 63) | 128); bytes.push((c & 63) | 128); }
            }
            this.dataList.push(bytes);
        },
        isDark: function(row, col) { return this.modules[row][col]; },
        getModuleCount: function() { return this.moduleCount; },
        make: function() {
            this.moduleCount = this.typeNumber * 4 + 17;
            this.modules = new Array(this.moduleCount);
            for (let row = 0; row < this.moduleCount; row++) this.modules[row] = new Array(this.moduleCount).fill(null);
            this.setupPositionProbePattern(0, 0);
            this.setupPositionProbePattern(this.moduleCount - 7, 0);
            this.setupPositionProbePattern(0, this.moduleCount - 7);
            this.setupPositionAdjustPattern();
            this.setupTimingPattern();
            this.setupTypeInfo(true, 0);

            const buffer = new QRBitBuffer();
            for (let i = 0; i < this.dataList.length; i++) {
                const data = this.dataList[i];
                buffer.put(QRMode.MODE_8BIT_BYTE, 4);
                buffer.put(data.length, 8);
                for (let j = 0; j < data.length; j++) buffer.put(data[j], 8);
            }
            const rsBlock = RS_BLOCK_TABLE[this.typeNumber];
            const totalDataCount = rsBlock[0] * rsBlock[2];
            if (buffer.length + 4 <= totalDataCount * 8) buffer.put(0, 4);
            while (buffer.length % 8 != 0) buffer.putBit(false);
            while (buffer.length < totalDataCount * 8) {
                buffer.put(0xEC, 8);
                if (buffer.length < totalDataCount * 8) buffer.put(0x11, 8);
            }
            this.mapData(buffer, rsBlock);
        },
        setupPositionProbePattern: function(row, col) {
            for (let r = -1; r <= 7; r++) {
                if (row + r <= -1 || this.moduleCount <= row + r) continue;
                for (let c = -1; c <= 7; c++) {
                    if (col + c <= -1 || this.moduleCount <= col + c) continue;
                    const isEdge = (0 <= r && r <= 6 && (c == 0 || c == 6)) || (0 <= c && c <= 6 && (r == 0 || r == 6));
                    this.modules[row + r][col + c] = isEdge || (2 <= r && r <= 4 && 2 <= c && c <= 4);
                }
            }
        },
        setupTimingPattern: function() {
            for (let r = 8; r < this.moduleCount - 8; r++) { if (this.modules[r][6] === null) this.modules[r][6] = (r % 2 == 0); }
            for (let c = 8; c < this.moduleCount - 8; c++) { if (this.modules[6][c] === null) this.modules[6][c] = (c % 2 == 0); }
        },
        setupPositionAdjustPattern: function() {
            const pos = QRUtil.PATTERN_POSITION_TABLE[this.typeNumber - 1];
            if (!pos) return;
            for (let i = 0; i < pos.length; i++) {
                for (let j = 0; j < pos.length; j++) {
                    const row = pos[i], col = pos[j];
                    if (this.modules[row][col] !== null) continue;
                    for (let r = -2; r <= 2; r++) {
                        for (let c = -2; c <= 2; c++) this.modules[row + r][col + c] = (Math.abs(r) == 2 || Math.abs(c) == 2 || (r == 0 && c == 0));
                    }
                }
            }
        },
        setupTypeInfo: function(test, maskPattern) {
            const bits = QRUtil.getBCHTypeInfo((0 << 3) | maskPattern);
            for (let i = 0; i < 15; i++) {
                const mod = (!test && ((bits >> i) & 1) == 1);
                if (i < 6) this.modules[i][8] = mod;
                else if (i < 8) this.modules[i + 1][8] = mod;
                else this.modules[this.moduleCount - 15 + i][8] = mod;
                if (i < 8) this.modules[8][this.moduleCount - i - 1] = mod;
                else if (i < 9) this.modules[8][15 - i - 1 + 1] = mod;
                else this.modules[8][15 - i - 1] = mod;
            }
            this.modules[this.moduleCount - 8][8] = !test;
        },
        mapData: function(data, rsBlock) {
            const count = rsBlock[0], totalCount = rsBlock[1], dataCount = rsBlock[2], ecCount = totalCount - dataCount;
            const rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount), rawBlocks = [];
            let offset = 0;
            for (let i = 0; i < count; i++) {
                const rawData = [];
                for (let j = 0; j < dataCount; j++) rawData.push(data.buffer[offset + j]);
                offset += dataCount;
                const rawPoly = new QRPolynomial(rawData, ecCount), modPoly = rawPoly.mod(rsPoly), ecData = new Array(ecCount).fill(0);
                for (let j = 0; j < modPoly.getLength(); j++) ecData[j + ecCount - modPoly.getLength()] = modPoly.get(j);
                rawBlocks.push({ data: rawData, ec: ecData });
            }
            const interleaved = [];
            for (let i = 0; i < dataCount; i++) { for (let j = 0; j < count; j++) interleaved.push(rawBlocks[j].data[i]); }
            for (let i = 0; i < ecCount; i++) { for (let j = 0; j < count; j++) interleaved.push(rawBlocks[j].ec[i]); }

            let inc = -1, row = this.moduleCount - 1, bitIndex = 7, byteIndex = 0;
            for (let col = this.moduleCount - 1; col > 0; col -= 2) {
                if (col == 6) col--;
                while (true) {
                    for (let c = 0; c < 2; c++) {
                        if (this.modules[row][col - c] === null) {
                            let dark = false;
                            if (byteIndex < interleaved.length) dark = (((interleaved[byteIndex] >>> bitIndex) & 1) == 1);
                            if (QRUtil.getMask(QRMaskPattern.PATTERN000, row, col - c)) dark = !dark;
                            this.modules[row][col - c] = dark;
                            bitIndex--;
                            if (bitIndex == -1) { bitIndex = 7; byteIndex++; }
                        }
                    }
                    row += inc;
                    if (row < 0 || this.moduleCount <= row) { row -= inc; inc = -inc; break; }
                }
            }
        }
    };

    window.generateBinderyQrSvg = function(text, size = 200) {
        if (!text) return '';
        let type = 1;
        const len = text.length;
        if (len <= 14) type = 1;
        else if (len <= 26) type = 2;
        else if (len <= 42) type = 3;
        else if (len <= 62) type = 4;
        else if (len <= 84) type = 5;
        else if (len <= 106) type = 6;
        else if (len <= 122) type = 7;
        else if (len <= 150) type = 8;
        else type = 10;

        try {
            const qr = new QRCodeModel(type);
            qr.addData(text);
            qr.make();
            const count = qr.getModuleCount(), margin = 4, total = count + margin * 2, cellSize = size / total;
            let d = '';
            for (let r = 0; r < count; r++) {
                for (let c = 0; c < count; c++) {
                    if (qr.isDark(r, c)) {
                        const x = (c + margin) * cellSize, y = (r + margin) * cellSize;
                        d += `M${x.toFixed(2)},${y.toFixed(2)}h${cellSize.toFixed(2)}v${cellSize.toFixed(2)}h-${cellSize.toFixed(2)}z `;
                    }
                }
            }
            return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="display:block; border-radius:8px;"><rect width="${size}" height="${size}" fill="#ffffff" rx="8"/><path fill="#000000" d="${d}"/></svg>`;
        } catch (e) {
            console.error('[BinderyQREngine] 生成 SVG 二维码异常:', e);
            return '';
        }
    };
})();
