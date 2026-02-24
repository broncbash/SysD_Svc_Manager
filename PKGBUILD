# Maintainer: broncbash	 
pkgname=SysD_Svc_Manager
pkgver=1.0.0
pkgrel=1
pkgdesc="Graphical GTK3 manager for systemd system and user services"
arch=('any')
url="https://github.com/broncbash/SysD_Svc_Manager.git"
license=('MIT')
depends=(
    'python'
    'python-gobject'
    'gtk3'
    'polkit'
)
optdepends=(
    'ttf-jetbrains-mono: preferred monospace font for the UI'
    'polkit-gnome: polkit authentication agent for GNOME/i3/sway'
    'lxqt-policykit: polkit authentication agent for LXQt'
)
source=("$pkgname-$pkgver.tar.gz::https://github.com/broncbash/$pkgname/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"

    # Main executable
    install -Dm755 systemd-manager.py "$pkgdir/usr/bin/systemd-manager"

    # Icons
    install -Dm644 systemd-manager.svg \
        "$pkgdir/usr/share/icons/hicolor/scalable/apps/systemd-manager.svg"
    install -Dm644 systemd-manager.png \
        "$pkgdir/usr/share/icons/hicolor/128x128/apps/systemd-manager.png"

    # Desktop entry
    install -Dm644 systemd-manager.desktop \
        "$pkgdir/usr/share/applications/systemd-manager.desktop"

    # License
    install -Dm644 LICENSE \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"

    # Optional: README
    install -Dm644 README.md \
        "$pkgdir/usr/share/doc/$pkgname/README.md"
}
