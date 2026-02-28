# -*- coding: utf-8 -*-
# @Time    : 2026/2/28 9:35
# @Author  : Cocktail_py

import random
import time

from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent



def get_random_device_info():
    """生成最新的、真实的设备信息和UA"""
    ua = UserAgent(browsers=['chrome'], os=['windows', 'macos', 'android', 'ios'], min_version=120)
    device_type = random.choice(['desktop', 'mobile'])

    if device_type == 'desktop':
        os_type = random.choice(['windows', 'macos'])
        screen_resolution = random.choice(['1920x1080', '2560x1440', '1366x768'])
        pixel_ratio = random.choice([1.0, 1.25, 1.5, 2.0])
    else:
        os_type = random.choice(['android', 'ios'])
        if os_type == 'android':
            screen_resolution = random.choice(['1080x2340', '1440x3200', '1080x2400'])
            pixel_ratio = random.choice([2.0, 2.5, 3.0])
        else:
            screen_resolution = random.choice(['1179x2556', '1290x2796', '1024x1366'])
            pixel_ratio = random.choice([2.0, 3.0])

    return {
        'ua': ua.chrome,
        'device_type': device_type,
        'os_type': os_type,
        'screen_resolution': screen_resolution,
        'pixel_ratio': pixel_ratio
    }


def launch_browser(device_info):
    """启动深度伪装的Playwright浏览器"""
    p = sync_playwright().start()

    # 解析设备信息
    width, height = map(int, device_info['screen_resolution'].split('x'))

    # 启动浏览器，设置基础伪装参数
    browser = p.chromium.launch(
        headless=False,  # 新手先开有头模式，调试方便，稳定后再开无头模式
        slow_mo=random.randint(100, 300),  # 随机延迟操作，模拟真实用户
        args=[
            '--disable-blink-features=AutomationControlled',  # 禁用自动化控制标识
            '--disable-infobars',  # 禁用提示栏
            '--disable-extensions',  # 禁用扩展
            '--disable-dev-shm-usage',  # 解决Linux下Chrome崩溃的问题
            '--no-sandbox',  # 禁用沙箱
            '--disable-setuid-sandbox',  # 禁用SUID沙箱
            '--disable-gpu',  # 禁用GPU，无头模式下必须加
            '--window-size={},{}'.format(width, height),  # 设置窗口大小
            '--user-agent={}'.format(device_info['ua']),  # 设置UA
        ]
    )

    # 创建上下文，设置更多基础伪装参数
    context = browser.new_context(
        viewport={'width': width, 'height': height},  # 设置视口大小
        user_agent=device_info['ua'],  # 再次设置UA
        device_scale_factor=device_info['pixel_ratio'],  # 设置像素比
        is_mobile=device_info['device_type'] == 'mobile',  # 设置是否为移动设备
        has_touch=device_info['device_type'] == 'mobile',  # 设置是否有触摸功能
        locale='zh-CN',  # 设置语言为中文
        timezone_id='Asia/Shanghai',  # 设置时区为上海
        permissions=['geolocation'],  # 禁用地理位置权限
        geolocation=None,  # 再次禁用地理位置
        color_scheme='light',  # 设置颜色方案为浅色
        reduced_motion='no-preference',  # 设置减少动作为无偏好
        forced_colors='none',  # 设置强制颜色为无
        accept_downloads=False,  # 禁用下载
        java_script_enabled=True,  # 必须开启JavaScript
    )

    # 创建页面
    page = context.new_page()

    # 添加深度伪装脚本
    randomize_canvas_fingerprint(page)
    randomize_webgl_fingerprint(page)
    disable_webrtc_fingerprint(page)

    return p, browser, context, page


def randomize_canvas_fingerprint(page):
    """随机化Canvas指纹"""
    page.add_init_script("""
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, options) {
        const ctx = originalGetContext.call(this, type, options);
        if (type === '2d') {
            const originalLineWidth = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'lineWidth');
            Object.defineProperty(CanvasRenderingContext2D.prototype, 'lineWidth', {
                set: function(value) {
                    originalLineWidth.set.call(this, value + Math.random() * 0.5 - 0.25);
                },
                get: originalLineWidth.get
            });

            const originalFillStyle = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'fillStyle');
            Object.defineProperty(CanvasRenderingContext2D.prototype, 'fillStyle', {
                set: function(value) {
                    if (typeof value === 'string' && value.startsWith('#')) {
                        let r = parseInt(value.slice(1, 3), 16);
                        let g = parseInt(value.slice(3, 5), 16);
                        let b = parseInt(value.slice(5, 7), 16);
                        r = Math.max(0, Math.min(255, r + Math.floor(Math.random() * 5 - 2)));
                        g = Math.max(0, Math.min(255, g + Math.floor(Math.random() * 5 - 2)));
                        b = Math.max(0, Math.min(255, b + Math.floor(Math.random() * 5 - 2)));
                        value = '#' + r.toString(16).padStart(2, '0') + g.toString(16).padStart(2, '0') + b.toString(16).padStart(2, '0');
                    }
                    originalFillStyle.set.call(this, value);
                },
                get: originalFillStyle.get
            });

            const originalFont = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'font');
            Object.defineProperty(CanvasRenderingContext2D.prototype, 'font', {
                set: function(value) {
                    const match = value.match(/(\\d+)(px|pt|em)/);
                    if (match) {
                        let size = parseInt(match[1]);
                        size = Math.max(8, Math.min(72, size + Math.floor(Math.random() * 3 - 1)));
                        value = value.replace(match[0], size + match[2]);
                    }
                    originalFont.set.call(this, value);
                },
                get: originalFont.get
            });
        }
        return ctx;
    };

    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
        let dataURL = originalToDataURL.call(this, type, quality);
        if (dataURL.startsWith('data:image/png;base64,')) {
            const base64 = dataURL.slice(22);
            const randomChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
            const modifiedBase64 = base64.slice(0, -5) + Array.from({length: 5}, () => randomChars[Math.floor(Math.random() * randomChars.length)]).join('');
            dataURL = 'data:image/png;base64,' + modifiedBase64;
        }
        return dataURL;
    };
    """)


def randomize_webgl_fingerprint(page):
    """随机化WebGL指纹"""
    page.add_init_script("""
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, options) {
        const ctx = originalGetContext.call(this, type, options);
        if (type === 'webgl' || type === 'webgl2') {
            const originalGetParameter = ctx.getParameter;
            ctx.getParameter = function(pname) {
                if (pname === ctx.RENDERER) {
                    const renderers = [
                        'NVIDIA GeForce RTX 3080/PCIe/SSE2',
                        'NVIDIA GeForce RTX 4090/PCIe/SSE2',
                        'AMD Radeon RX 7900 XTX/PCIe/SSE2',
                        'Intel(R) UHD Graphics 770',
                        'Apple M2 Max GPU',
                    ];
                    return renderers[Math.floor(Math.random() * renderers.length)];
                }
                if (pname === ctx.VENDOR) {
                    const vendors = ['NVIDIA Corporation', 'AMD', 'Intel Inc.', 'Apple'];
                    return vendors[Math.floor(Math.random() * vendors.length)];
                }
                if (pname === ctx.VERSION) {
                    const versions = ['WebGL 1.0 (OpenGL ES 2.0 Chromium)', 'WebGL 2.0 (OpenGL ES 3.0 Chromium)'];
                    return versions[Math.floor(Math.random() * versions.length)];
                }
                if (pname === ctx.SHADING_LANGUAGE_VERSION) {
                    const versions = ['WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)', 'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)'];
                    return versions[Math.floor(Math.random() * versions.length)];
                }
                return originalGetParameter.call(this, pname);
            };

            const originalGetSupportedExtensions = ctx.getSupportedExtensions;
            ctx.getSupportedExtensions = function() {
                const extensions = originalGetSupportedExtensions.call(this);
                const numToRemove = Math.floor(Math.random() * 3) + 1;
                for (let i = 0; i < numToRemove; i++) {
                    if (extensions.length > 0) {
                        const indexToRemove = Math.floor(Math.random() * extensions.length);
                        extensions.splice(indexToRemove, 1);
                    }
                }
                return extensions;
            };
        }
        return ctx;
    };
    """)


def disable_webrtc_fingerprint(page):
    """彻底禁用WebRTC指纹"""
    page.add_init_script("""
    Object.defineProperty(navigator, 'webkitRTCPeerConnection', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'mozRTCPeerConnection', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'RTCPeerConnection', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'webkitGetUserMedia', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'mozGetUserMedia', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'getUserMedia', {
        value: undefined,
        writable: false,
        configurable: false
    });
    Object.defineProperty(navigator, 'mediaDevices', {
        value: undefined,
        writable: false,
        configurable: false
    });
    """)


def random_delay(min_delay=100, max_delay=500):
    """随机延迟操作"""
    time.sleep(random.uniform(min_delay / 1000, max_delay / 1000))


def simulate_real_mouse_click(page, selector):
    """模拟真实的鼠标移动和点击"""
    element = page.wait_for_selector(selector, timeout=10000)
    box = element.bounding_box()
    if not box:
        raise Exception(f"元素 {selector} 未找到或不可见")

    center_x = box['x'] + box['width'] / 2
    center_y = box['y'] + box['height'] / 2

    nearby_x = center_x + random.randint(-50, 50)
    nearby_y = center_y + random.randint(-50, 50)
    page.mouse.move(nearby_x, nearby_y, steps=random.randint(10, 20))
    random_delay(100, 300)

    page.mouse.move(center_x, center_y, steps=random.randint(20, 40))
    random_delay(200, 500)

    page.mouse.click(center_x, center_y)
    random_delay(300, 700)





def main():
    """主函数"""
    # 生成随机设备信息
    device_info = get_random_device_info()
    print(f"使用设备信息：{device_info}")

    # 启动浏览器
    p, browser, context, page = launch_browser(device_info)
    TARGET_URL = "https://xxx"
    # 打开目标URL
    print(f"正在打开目标URL：{TARGET_URL}")
    page.goto(TARGET_URL, timeout=30000)


if __name__ == "__main__":
    main()


