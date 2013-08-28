
%global qt_module qtwebkit

Summary: Qt5 - QtWebKit components
Name:    qt5-qtwebkit
Version: 5.1.1
Release: 1%{?dist}

# See LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt, for details
# See also http://qt-project.org/doc/qt-5.0/qtdoc/licensing.html
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url: http://qt-project.org/
Source0: http://download.qt-project.org/official_releases/qt/5.1/%{version}/submodules/%{qt_module}-opensource-src-%{version}.tar.xz

# qt5-qtjsbackend (and qtdeclarative) supports only ix86, x86_64 and arm , and so do we here
ExclusiveArch: %{ix86} x86_64 %{arm}

# Search /usr/lib{,64}/mozilla/plugins-wrapped for browser plugins too
Patch1: webkit-qtwebkit-2.2-tp1-pluginpath.patch

# smaller debuginfo s/-g/-g1/ (debian uses -gstabs) to avoid 4gb size limit
Patch3: qtwebkit-opensource-src-5.0.1-debuginfo.patch

# tweak linker flags to minimize memory usage on "small" platforms
Patch4: qtwebkit-save_memory.patch

# use unbundled system angleproject library
#define system_angle 1
# NEEDS REBASE for 5.1 -- rex
Patch5: qtwebkit-opensource-src-5.0.2-system_angle.patch
# Fix compilation against latest ANGLE
# https://bugs.webkit.org/show_bug.cgi?id=109127
Patch6: webkit-commit-142567.patch
%if 0%{?system_angle}
BuildRequires: angleproject-devel angleproject-static
%endif


BuildRequires: qt5-qtbase-devel >= %{version}
BuildRequires: qt5-qtdeclarative-devel >= %{version}

BuildRequires: bison
BuildRequires: chrpath
BuildRequires: flex
BuildRequires: gperf
BuildRequires: libicu-devel
BuildRequires: libjpeg-devel
BuildRequires: pkgconfig(gio-2.0) pkgconfig(glib-2.0)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(gl)
# gstreamer media support
BuildRequires: pkgconfig(gstreamer-0.10) pkgconfig(gstreamer-app-0.10)
BuildRequires: pkgconfig(icu-i18n)
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(libpcre)
BuildRequires: pkgconfig(libwebp)
BuildRequires: pkgconfig(libxslt)
BuildRequires: pkgconfig(sqlite3)
BuildRequires: pkgconfig(xcomposite) pkgconfig(xrender)
BuildRequires: perl perl(version) perl(Digest::MD5)
BuildRequires: ruby
BuildRequires: zlib-devel

%{?_qt5_version:Requires: qt5-qtbase%{?_isa} >= %{_qt5_version}}

##upstream patches


%description
%{summary}

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}
Requires: qt5-qtdeclarative-devel%{?_isa}
%description devel
%{summary}.


%prep
%setup -q -n qtwebkit-opensource-src-%{version}%{?pre:-%{pre}}

%patch1 -p1 -b .pluginpath
%patch3 -p1 -b .debuginfo
%patch4 -p1 -b .save_memory
%if 0%{?system_angle}
#patch5 -p1 -b .system_angle
%patch6 -p1 -b .svn142567
%endif

echo "nuke bundled code..."
# nuke bundled code
mkdir Source/ThirdParty/orig
mv Source/ThirdParty/{glu/,gtest/,gyp/,mt19937ar.c,qunit/} \
   Source/ThirdParty/orig/

%if 0%{?system_angle}
mv Source/ThirdParty/ANGLE/ \
   Source/ThirdParty/orig/
%endif


%build
%{_qt5_qmake} %{?system_angle:DEFINES+=USE_SYSTEM_ANGLE=1}

make %{?_smp_mflags}


%install

make install INSTALL_ROOT=%{buildroot}

## .prl file love (maybe consider just deleting these -- rex
# nuke dangling reference(s) to %%buildroot, excessive (.la-like) libs
sed -i \
  -e "/^QMAKE_PRL_BUILD_DIR/d" \
  -e "/^QMAKE_PRL_LIBS/d" \
  %{buildroot}%{_qt5_libdir}/*.prl

## unpackaged files
# .la files, die, die, die.
rm -fv %{buildroot}%{_qt5_libdir}/lib*.la

## kill rpath's
pushd %{buildroot}
for remove_rpath in \
  %{_qt5_libexecdir}/QtWebPluginProcess \
  %{_qt5_libexecdir}/QtWebProcess \
  %{_qt5_archdatadir}/qml/QtWebKit/libqmlwebkitplugin.so \
  %{_qt5_archdatadir}/qml/QtWebKit/experimental/libqmlwebkitexperimentalplugin.so \
; do
chrpath --list   %{buildroot}$remove_rpath
chrpath --delete %{buildroot}$remove_rpath
done
popd


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc Source/WebCore/LICENSE*
%doc ChangeLog VERSION
%{_qt5_libdir}/libQt5WebKit.so.5*
%{_qt5_libdir}/libQt5WebKitWidgets.so.5*
%{_qt5_libexecdir}/QtWebPluginProcess
%{_qt5_libexecdir}/QtWebProcess
%{_qt5_archdatadir}/qml/QtWebKit/

%files devel
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5*.so
%{_qt5_libdir}/libQt5*.prl
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri


%changelog
* Wed Aug 28 2013 Rex Dieter <rdieter@fedoraproject.org> 5.1.1-1
- 5.1.1

* Tue Aug 20 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-8
- qt5-qtjsbackend only supports ix86, x86_64 and arm

* Fri Aug 02 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-7
- use bundled angleproject (until system version passes review)

* Fri Jun 21 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-6
- %%doc ChangeLog VERSION
- %%doc Source/WebCore/LICENSE*
- squash more rpaths

* Fri May 17 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-5
- unbundle angleproject code

* Wed May 15 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-4
- BR: perl(version) perl(Digest::MD5) pkgconfig(xslt)
- deal with bundled code
- add (commented) upstream link http://qt-project.org/doc/qt-5.0/qtdoc/licensing.html
  to clarify licensing

* Thu May 09 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-3
- -devel: Requires: qt5-qtdeclarative-devel

* Fri Apr 12 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-2
- BR: qt5-qtdeclarative-devel

* Thu Apr 11 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-1
- 5.0.2

* Mon Feb 25 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-2
- .prl love
- BR: pkgconfig(gl)

* Sat Feb 23 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-1
- first try

