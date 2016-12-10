
%global qt_module qtwebkit

%global _hardened_build 1

Summary: Qt5 - QtWebKit components
Name: qt5-qtwebkit
Version: 5.7.1
Release: 2%{?dist}

# See LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt, for details
# See also http://qt-project.org/doc/qt-5.0/qtdoc/licensing.html
License: LGPLv2 with exceptions or GPLv3 with exceptions
Source0: http://download.qt.io/official_releases/qt/5.7/%{version}/latest_src/submodules/qtwebkit-opensource-src-%{version}.tar.xz

## downstream patches
# Search /usr/lib{,64}/mozilla/plugins-wrapped for browser plugins too
Patch1: qtwebkit-opensource-src-5.2.0-pluginpath.patch

# smaller debuginfo s/-g/-g1/ (debian uses -gstabs) to avoid 4gb size limit
Patch3: qtwebkit-opensource-src-5.0.1-debuginfo.patch

# tweak linker flags to minimize memory usage on "small" platforms
Patch4: qtwebkit-opensource-src-5.2.0-save_memory.patch

# Add AArch64 support
Patch7: 0001-Add-ARM-64-support.patch

# truly madly deeply no rpath please, kthxbye
Patch8: qtwebkit-opensource-src-5.2.1-no_rpath.patch

BuildRequires: qt5-qtbase-devel >= %{version}
BuildRequires: pkgconfig(Qt5Qml) >= %{version}
%if ! 0%{?bootstrap}
BuildRequires: pkgconfig(Qt5Sensors)
BuildRequires: pkgconfig(Qt5Location)
BuildRequires: pkgconfig(Qt5WebChannel)
%endif
BuildRequires: bison
BuildRequires: flex
BuildRequires: gperf
BuildRequires: libicu-devel
BuildRequires: libjpeg-devel
BuildRequires: pkgconfig(gio-2.0) pkgconfig(glib-2.0)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(gl)
# gstreamer media support
%if 0%{?fedora} > 20 || 0%{?rhel} > 7
BuildRequires: pkgconfig(gstreamer-1.0) pkgconfig(gstreamer-app-1.0)
%else
BuildRequires: pkgconfig(gstreamer-0.10) pkgconfig(gstreamer-app-0.10)
%endif
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(libpcre)
BuildRequires: pkgconfig(libudev)
%if 0%{?fedora} || 0%{?rhel} > 6
BuildRequires: pkgconfig(libwebp)
%endif
BuildRequires: pkgconfig(libxslt)
BuildRequires: pkgconfig(sqlite3)
BuildRequires: pkgconfig(xcomposite) pkgconfig(xrender)
BuildRequires: perl perl(version)
BuildRequires: perl(Digest::MD5) perl(Text::ParseWords) perl(Getopt::Long)
BuildRequires: ruby rubypick rubygems
BuildRequires: zlib-devel

BuildRequires: qt5-qtbase-private-devel
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires:  qt5-qtdeclarative-private-devel
%{?_qt5:Requires: qt5-qtdeclarative%{?_isa} = %{_qt5_version}}

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

%if 0%{?docs}
%package doc
Summary: API documentation for %{name}
BuildRequires: qt5-qdoc
BuildRequires: qt5-qhelpgenerator
BuildArch: noarch
%description doc
%{summary}.
%endif


%prep
%setup -q -n %{qt_module}-opensource-src-%{version}

%patch1 -p1 -b .pluginpath
%patch3 -p1 -b .debuginfo
%patch4 -p1 -b .save_memory
%patch7 -p1 -b .aarch64
%patch8 -p1 -b .no_rpath

echo "nuke bundled code..."
# nuke bundled code
mkdir Source/ThirdParty/orig
mv Source/ThirdParty/{gtest/,qunit/} \
   Source/ThirdParty/orig/

if [ ! -d include ]; then
syncqt.pl -version %{version} Source/sync.profile
fi


%build
mkdir %{_target_platform}
pushd %{_target_platform}

%{qmake_qt5} .. \
%ifnarch %{arm} %{ix86} x86_64
    DEFINES+=ENABLE_JIT=0 DEFINES+=ENABLE_YARR_JIT=0
%endif

# workaround, disable parallel compilation as it fails to compile in brew
#make %{?_smp_mflags}
make -j3

%if 0%{?docs}
make %{?_smp_mflags} docs
%endif
popd


%install
make install INSTALL_ROOT=%{buildroot} -C %{_target_platform}

%if 0%{?docs}
make install_docs INSTALL_ROOT=%{buildroot} -C %{_target_platform}
%endif

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license Source/WebCore/LICENSE*
%doc ChangeLog* VERSION
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

%if 0%{?docs}
%files doc
%{_qt5_docdir}/qtwebkit.qch
%{_qt5_docdir}/qtwebkit/
%endif


%changelog
* Sat Dec 10 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-2
- drop BR: cmake (handled by qt5-rpm-macros now)
- 5.7.1 dec5 snapshot

* Wed Nov 09 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.1-1
- New upstream version

* Mon Jul 04 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-2
- Compiled with gcc

* Wed Jun 15 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-1
- Qt 5.7.0 release ( non git, official package )

* Tue Jun 14 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.1-2.b889f46git
- rebuild (glibc)

* Thu Jun 09 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.1-1.b889f46git
- 5.6.1 branch snapshot, plus a couple post-5.6.1 5.6 branch fixes

* Thu Jun 09 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-9
- rebuild (qtbase)

* Wed May 18 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-8
- use pristine upstream (community) sources

* Wed Apr 20 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-7
- rebuild (icu)

* Sun Apr 17 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-6
- BR: qt5-qtbase-private-devel qt5-qtdeclarative-private-devel

* Fri Apr 15 2016 David Tardon <dtardon@redhat.com> - 5.6.0-5
- rebuild for ICU 57.1

* Wed Apr  6 2016 Peter Robinson <pbrobinson@fedoraproject.org> 5.6.0-4
- Update ruby deps to ensure all bits are present

* Sun Mar 20 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-3
- rebuild

* Fri Mar 18 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-2
- rebuild

* Mon Mar 14 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-1
- 5.6.0 final release

* Mon Feb 29 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.12.rc
- fix sources

* Wed Feb 24 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.11.rc
- Fix the trap caused by rpmdev-bumpspec

* Tue Feb 23 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.10.rc
- Update to final RC

* Mon Feb 15 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.9
- Update RC release

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.6.0-0.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 28 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.7
- BR: cmake, use %%license

* Mon Dec 28 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 5.6.0-0.6
- Rebuilt for libwebp soname bump

* Sun Dec 13 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.5
- Update beta code

* Fri Dec 11 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-0.4
- restore bootstrap macro, omit more optional BR's/features in bootstrap mode
- drop (unused) system_angle support
- include -qdoc builddep only in -doc subpkg

* Thu Dec 10 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.3
- Official beta release

* Sun Dec 06 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.2
- (re)add bootstrap macro support

* Tue Nov 03 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.1
- Start to implement 5.6.0 beta

* Wed Oct 28 2015 David Tardon <dtardon@redhat.com> - 5.5.1-4
- rebuild for ICU 56.1

* Fri Oct 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.1-3
- drop (unused) system_angle support/patches

* Thu Oct 15 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-2
- Update to final release 5.5.1

* Tue Sep 29 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-1
- Update to Qt 5.5.1 RC1

* Wed Jul 29 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-4
- -docs: BuildRequires: qt5-qhelpgenerator, standardize bootstrapping

* Thu Jul 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-3
- tighten deps (#1233829)

* Mon Jul 13 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.5.0-2
- add 5.5.0-1 changelog
- BR: qt5-qtwebchannel-devel
- (re)enable docs

* Wed Jul 1 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-1
- New final upstream release Qt 5.5.0

* Thu Jun 25 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.2.rc
- Update for official RC1 released packages

* Wed Jun 03 2015 Jan Grulich <jgrulich@redhat.com> - 5.4.2-1
- 5.4.2

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 5.4.1-6
- Rebuilt for GCC 5 C++11 ABI change

* Fri Apr 03 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.1-5
- -doc: drop dep on main pkg, not strictly required

* Mon Mar 23 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.1-4
- QtWebKit logs visited URLs to WebpageIcons.db in private browsing mode (#1204795,#1204798)

* Wed Mar 18 2015 Than Ngo <than@redhat.com> - 5.4.1-3
- fix build failure with new gcc5

* Fri Feb 27 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.4.1-2
- rebuild (gcc5)

* Tue Feb 24 2015 Jan Grulich <jgrulich@redhat.com> 5.4.1-1
- 5.4.1

* Tue Feb 17 2015 Than Ngo <than@redhat.com> 5.4.0-4
- fix GMutexLocker build problem

* Tue Feb 17 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-3
- rebuild (gcc5)

* Mon Jan 26 2015 David Tardon <dtardon@redhat.com> - 5.4.0-2
- rebuild for ICU 54.1

* Wed Dec 10 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-1
- 5.4.0 (final)

* Fri Nov 28 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.5.rc
- 5.4.0-rc

* Tue Nov 18 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.4.beta
- use gst1 only fc21+ (and el8+) only

* Mon Nov 03 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.3.beta
- fix hardening, use new %%qmake_qt5 macro

* Sat Nov 01 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.2.beta
- enable hardened build, out-of-src tree build

* Sat Oct 18 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.1.beta
- 5.4.0-beta

* Tue Sep 16 2014 Rex Dieter <rdieter@fedoraproject.org> 5.3.2-1
- 5.3.2

* Tue Aug 26 2014 David Tardon <dtardon@redhat.com> - 5.3.1-3
- rebuild for ICU 53.1

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 17 2014 Jan Grulich <jgrulich@redhat.com> - 5.3.1-1
- 5.3.1

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Jan Grulich <jgrulich@redhat.com> 5.3.0-1
- 5.3.0

* Mon May 05 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-4
- use standard (same as qtbase) .prl sanitation

* Fri May 02 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-3
- no rpath, drop chrpath hacks
- BR: qt5-qtlocation qt5-qtsensors

* Wed Feb 12 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-2
- rebuild (libicu)

* Wed Feb 05 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-1
- 5.2.1

* Sun Feb 02 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-3
- Add AArch64 support to qtwebkit (#1056160)

* Wed Jan 01 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-2
- rebuild (libwebp)

* Thu Dec 12 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-1
- 5.2.0

* Mon Dec 02 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.10.rc1
- 5.2.0-rc1

* Thu Nov 28 2013 Dan Horák <dan[at]danny.cz> 5.2.0-0.6.beta1
- disable JIT on secondary arches, fix build with JIT disabled (#1034940)

* Mon Nov 25 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.5.beta1
- enable -doc only on primary archs (allow secondary bootstrap)

* Sat Nov 09 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.4.beta1
- rebuild (arm/qreal)

* Thu Oct 24 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.3.beta1
- 5.2.0-beta1

* Wed Oct 16 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.2.alpha
- bootstrap ppc

* Wed Oct 02 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.1.alpha
- 5.2.0-alpha
- -doc subpkg
- use gstreamer1 (where available)

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

