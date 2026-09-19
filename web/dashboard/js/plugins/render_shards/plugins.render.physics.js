/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - 3D Hover Physics & Compute Routing Shard
 * 职责：能力节点卡片 3D 视差物理微动效 (init3DHoverPhysics) 与算力中心路由跳转/高亮联动。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.init3DHoverPhysics = () => {
        document.querySelectorAll('.shield-pod').forEach(pod => {
            if (pod.dataset.has3DPhysics) return;
            pod.dataset.has3DPhysics = 'true';

            pod.addEventListener('mousemove', (e) => {
                const rect = pod.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const tiltX = (y - centerY) / 16;
                const tiltY = -(x - centerX) / 16;

                pod.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(4px)`;
                pod.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
                pod.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
            });

            pod.addEventListener('mouseleave', () => {
                pod.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
            });
        });
    };

    /**
     * ⚡ 从 AI 协议卡片一键路由跳转至算力中心并预选协议驱动创建单元
     */
    window.createComputeNodeFromProtocol = async (protocolId) => {
        window._pendingAddProtocolId = protocolId;
        if (typeof window.showView === 'function') {
            await window.showView('compute', 'infrastructure');
        } else if (typeof window.location !== 'undefined') {
            window.location.hash = '#/compute/infrastructure';
        }
        const checkAndOpenModal = () => {
            if (window.ComputeHandlers && typeof window.ComputeHandlers.showAddNodeModal === 'function') {
                window.ComputeHandlers.showAddNodeModal(protocolId);
                window._pendingAddProtocolId = null;
            }
        };
        setTimeout(checkAndOpenModal, 150);
    };

    /**
     * 🎯 从插件中心一键跳转至算力中心并高亮定位指定算力单元
     */
    window.locateAndHighlightComputeNode = async (nodeId) => {
        if (typeof window.showView === 'function') {
            await window.showView('compute', 'infrastructure');
        } else if (typeof window.location !== 'undefined') {
            window.location.hash = '#/compute/infrastructure';
        }
        setTimeout(() => {
            const targetCard = document.getElementById(`node-unit-${nodeId}`);
            if (targetCard) {
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                targetCard.style.transition = 'all 0.4s ease';
                targetCard.style.boxShadow = '0 0 24px rgba(0, 242, 255, 0.9), 0 0 48px rgba(0, 242, 255, 0.4)';
                targetCard.style.borderColor = 'var(--neon-cyan)';
                setTimeout(() => {
                    targetCard.style.boxShadow = '';
                    targetCard.style.borderColor = '';
                }, 2200);
            }
        }, 220);
    };

})();
