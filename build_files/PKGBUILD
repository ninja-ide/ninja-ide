# Submitted:  Federico Cinelli <cinelli.federico@gmail.com>
# Maintainer: Federico Cinelli <cinelli.federico@gmail.com>

pkgname=ninja-ide-git
pkgver=20130206
pkgrel=1
pkgdesc="Ninja Is Not Just Another Intergrated Development Environment - Latest git pull"
arch=('any')
url="http://ninja-ide.org"
license=('GPL')
depends=('python2' 'python2-distribute' 'python2-pyqt' 'git' 'python2-pyinotify')
install=$pkgname.install
provides=('ninja-ide-git')
conflicts=('ninja-ide')
replaces=('ninja-ide')
source=(ninja-ide-git.desktop)
md5sums=('384b13743f204b17ed3b87cc7d8df456')

_gitroot="git://github.com/ninja-ide/ninja-ide.git"
_gitname="ninja-ide"

build() {
  msg "Connecting to GIT server...."

  if  [ -d $_gitname ] ; then
    cd $_gitname && git pull origin
    msg "The local files are updated."
  else
    git clone $_gitroot $_gitname
  fi

  msg "GIT checkout done or server timeout"

  rm -rf "$srcdir/$_gitname-build"
  cp -r "$srcdir/$_gitname" "$srcdir/$_gitname-build"

  cd "$srcdir/$_gitname-build"
}

package() {
  cd "$srcdir/$_gitname-build"

  install -Dm644 "$srcdir/$pkgname.desktop" "$pkgdir/usr/share/applications/$pkgname.desktop"
  install -Dm644 "ninja_ide/img/icon.png" "$pkgdir/usr/share/pixmaps/$pkgname.png"

  sed -i 's|#!/usr/bin/env python|#!/usr/bin/env python2|' ninja-ide.py
  python2 setup.py install --root=$pkgdir/ --optimize=1
}
