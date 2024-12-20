#
# Conditional build:
%bcond_with	ffmpeg		# FFmpeg instead of GStreamer as generic media extractor
%bcond_with	gupnp		# GStreamer gupnp backend instead of discoverer
%bcond_with	icu		# ICU instead of enca for MP3 encoding detection
%bcond_with	landlock	# landlock sandboxing (requires kernel 5.13 and landlock enabled in LSM)
%bcond_without	rss		# RSS miner

%define		abiver	3.0
Summary:	Tracker miners and metadata extractors
Summary(pl.UTF-8):	Narzędzia wydobywania danych dla programu Tracker
Name:		localsearch
Version:	3.8.2
Release:	2
# see COPYING for details
License:	LGPL v2.1+ (libs), GPL v2+ (miners)
Group:		Applications
Source0:	https://download.gnome.org/sources/localsearch/3.8/%{name}-%{version}.tar.xz
# Source0-md5:	56dfb5a30b3ab5ba33939d9f6bc21016
URL:		https://gnome.pages.gitlab.gnome.org/localsearch/
BuildRequires:	NetworkManager-devel
BuildRequires:	asciidoc
# sha256sum
BuildRequires:	coreutils >= 6.0
BuildRequires:	dbus-devel >= 1.3.1
%{!?with_icu:BuildRequires:	enca-devel >= 1.9}
BuildRequires:	exempi-devel >= 2.1.0
# libavcodec libavformat libavutil
%{?with_ffmpeg:BuildRequires:	ffmpeg-devel >= 0.8.4}
BuildRequires:	gexiv2-devel
BuildRequires:	giflib-devel
BuildRequires:	glib2-devel >= 1:2.70.0
BuildRequires:	gstreamer-devel >= 1.20
BuildRequires:	gstreamer-plugins-base-devel >= 1.20
%if %{with gupnp}
BuildRequires:	gupnp-dlna-devel >= 0.9.4
BuildRequires:	gupnp-dlna-gst-devel >= 0.9.4
%endif
BuildRequires:	libblkid-devel
BuildRequires:	libcue-devel >= 2.0.0
BuildRequires:	libexif-devel >= 0.6
%{?with_rss:BuildRequires:	libgrss-devel >= 0.7}
BuildRequires:	libgsf-devel >= 1.14.24
BuildRequires:	libgxps-devel
%{?with_icu:BuildRequires:	libicu-devel >= 4.8.1.1}
BuildRequires:	libiptcdata-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libosinfo-devel >= 0.2.9
BuildRequires:	libpng-devel >= 0.89
%ifnarch alpha ia64 m68k parisc parisc64 riscv64 sh4 sparc sparcv9 sparc64
BuildRequires:	libseccomp-devel >= 2.0
%endif
BuildRequires:	libtiff-devel >= 4
BuildRequires:	libxml2-devel >= 1:2.6
BuildRequires:	libxslt-progs
%{?with_landlock:BuildRequires:	linux-libc-headers >= 7:5.13}
BuildRequires:	meson >= 0.51
BuildRequires:	ninja >= 1.5
BuildRequires:	pkgconfig
BuildRequires:	poppler-glib-devel >= 0.16.0
BuildRequires:	rpmbuild(macros) >= 2.011
BuildRequires:	tar >= 1:1.22
BuildRequires:	tinysparql-devel >= 3.8
BuildRequires:	totem-pl-parser-devel
BuildRequires:	upower-devel >= 0.9.0
BuildRequires:	xz
BuildRequires:	zlib-devel
Requires(post,preun):	systemd-units >= 1:250.1
Requires:	dbus >= 1.3.1
%{!?with_icu:Requires:	enca-libs >= 1.9}
Requires:	exempi >= 2.1.0
Requires:	glib2 >= 1:2.70.0
Requires:	gstreamer >= 1.20
Requires:	gstreamer-plugins-base >= 1.20
%if %{with gupnp}
Requires:	gupnp-dlna >= 0.9.4
Requires:	gupnp-dlna-gst >= 0.9.4
%endif
Requires:	libcue >= 2.0.0
Requires:	libexif >= 0.6
%{?with_rss:Requires:	libgrss >= 0.7}
Requires:	libgsf >= 1.14.24
Requires:	libosinfo >= 0.2.9
Requires:	libxml2 >= 1:2.6
Requires:	systemd-units >= 1:250.1
Requires:	tinysparql >= 3.8
%{?with_landlock:Requires:	uname(release) >= 5.13}
Obsoletes:	tracker3-miners < 3.8.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains various miners and metadata extractors for
tracker.

%description -l pl.UTF-8
Ten pakiet zawiera narzędzia wydobywania danych dla programu Tracker.

%package testutils
Summary:	Tracker 3 test utilities
Summary(pl.UTF-8):	Narzędzia testowe Trackera 3
Group:		Development/Tools
Requires:	dbus
Requires:	%{name} = %{version}-%{release}
Requires:	python3 >= 1:3.2
Requires:	python3-pygobject3 >= 3
Obsoletes:	tracker3-testutils < 3.8.0

%description testutils
Tracker 3 test utilities.

%description testutils -l pl.UTF-8
Narzędzia testowe Trackera 3.

%prep
%setup -q

%build
%meson build \
	--default-library=shared \
	-Dbattery_detection=upower \
	-Dcharset_detection=%{?with_icu:icu}%{!?with_icu:enca} \
	-Dfunctional_tests=false \
	-Dgeneric_media_extractor=%{?with_ffmpeg:libav}%{!?with_ffmpeg:gstreamer} \
	-Dgstreamer_backend=%{?with_gupnp:gupnp}%{!?with_gupnp:discoverer} \
	-Dlandlock=%{__enabled_disabled landlock} \
	%{?with_rss:-Dminer_rss=true} \
	-Dsystemd_user_services_dir=%{systemduserunitdir}

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%find_lang localsearch3

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with landlock}
%verifyscript
if ! grep -q -s '\<landlock\>' /sys/kernel/security/lsm ; then
	echo "LANDLOCK LSM not enabled in kernel"
fi
%endif

%post
%glib_compile_schemas
%systemd_user_post localsearch-3.service localsearch-control-3.service localsearch-writeback-3.service %{?with_rss:tracker-miner-rss-3.service}

%preun
%systemd_user_preun localsearch-3.service localsearch-control-3.service localsearch-writeback-3.service %{?with_rss:tracker-miner-rss-3.service}

%postun
%glib_compile_schemas

%files -f localsearch3.lang
%defattr(644,root,root,755)
%doc AUTHORS COPYING MAINTAINERS NEWS README.md
%attr(755,root,root) %{_bindir}/localsearch
%attr(755,root,root) %{_libexecdir}/localsearch-3
%attr(755,root,root) %{_libexecdir}/localsearch-control-3
%attr(755,root,root) %{_libexecdir}/localsearch-extractor-3
%attr(755,root,root) %{_libexecdir}/localsearch-writeback-3
%{systemduserunitdir}/localsearch-3.service
%{systemduserunitdir}/localsearch-control-3.service
%{systemduserunitdir}/localsearch-writeback-3.service
/etc/xdg/autostart/localsearch-3.desktop
%dir %{_libdir}/localsearch-%{abiver}
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/libtracker-extract.so
%dir %{_libdir}/localsearch-%{abiver}/extract-modules
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-abw.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-bmp.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-desktop.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-disc-generic.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-dummy.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-epub.so
# R: giflib
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-gif.so
# R: gstreamer gstreamer-plugins-base
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-gstreamer.so
# R: libxml2
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-html.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-icon.so
# R: libosinfo
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-iso.so
# R: libiptcdata libjpeg
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-jpeg.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-mp3.so
# R: libgsf
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-msoffice.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-msoffice-xml.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-oasis.so
# R: poppler-glib
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-pdf.so
# R: totem-plparser
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-playlist.so
# R: libpng
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-png.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-ps.so
# R: libgexiv2
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-raw.so
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-text.so
# R: libtiff
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-tiff.so
# R: libgxps
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/extract-modules/libextract-xps.so
%dir %{_libdir}/localsearch-%{abiver}/writeback-modules
# R: gstreamer gstreamer-plugins-base
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/writeback-modules/libwriteback-gstreamer.so
# R: exempi
%attr(755,root,root) %{_libdir}/localsearch-%{abiver}/writeback-modules/libwriteback-xmp.so
%{_datadir}/dbus-1/interfaces/org.freedesktop.Tracker3.Miner.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.Tracker3.Miner.Files.Index.xml
%{_datadir}/dbus-1/services/org.freedesktop.LocalSearch3.service
%{_datadir}/dbus-1/services/org.freedesktop.LocalSearch3.Control.service
%{_datadir}/dbus-1/services/org.freedesktop.LocalSearch3.Writeback.service
%{_datadir}/dbus-1/services/org.freedesktop.Tracker3.Miner.Files.service
%{_datadir}/dbus-1/services/org.freedesktop.Tracker3.Miner.Files.Control.service
%{_datadir}/dbus-1/services/org.freedesktop.Tracker3.Writeback.service
%{_datadir}/glib-2.0/schemas/org.freedesktop.Tracker3.Extract.gschema.xml
%{_datadir}/glib-2.0/schemas/org.freedesktop.Tracker3.FTS.gschema.xml
%{_datadir}/glib-2.0/schemas/org.freedesktop.Tracker3.Miner.Files.gschema.xml
%{_datadir}/glib-2.0/schemas/org.freedesktop.TrackerMiners3.enums.xml
%dir %{_datadir}/localsearch3
%dir %{_datadir}/localsearch3/domain-ontologies
%{_datadir}/localsearch3/domain-ontologies/default.rule
%dir %{_datadir}/localsearch3/extract-rules
# standalone (builtin?) rules
%{_datadir}/localsearch3/extract-rules/10-comics.rule
%{_datadir}/localsearch3/extract-rules/10-ebooks.rule
%{_datadir}/localsearch3/extract-rules/10-folder.rule
%{_datadir}/localsearch3/extract-rules/10-svg.rule
%{_datadir}/localsearch3/extract-rules/15-executable.rule
%{_datadir}/localsearch3/extract-rules/15-games.rule
# modules
%{_datadir}/localsearch3/extract-rules/10-abw.rule
%{_datadir}/localsearch3/extract-rules/10-bmp.rule
%{_datadir}/localsearch3/extract-rules/10-desktop.rule
%{_datadir}/localsearch3/extract-rules/10-epub.rule
%{_datadir}/localsearch3/extract-rules/10-gif.rule
%{_datadir}/localsearch3/extract-rules/10-html.rule
%{_datadir}/localsearch3/extract-rules/10-ico.rule
%{_datadir}/localsearch3/extract-rules/10-jpeg.rule
%{_datadir}/localsearch3/extract-rules/10-mp3.rule
%{_datadir}/localsearch3/extract-rules/10-msoffice.rule
%{_datadir}/localsearch3/extract-rules/10-oasis.rule
%{_datadir}/localsearch3/extract-rules/10-pdf.rule
%{_datadir}/localsearch3/extract-rules/10-png.rule
%{_datadir}/localsearch3/extract-rules/10-ps.rule
%{_datadir}/localsearch3/extract-rules/10-raw.rule
%{_datadir}/localsearch3/extract-rules/10-tiff.rule
%{_datadir}/localsearch3/extract-rules/10-xps.rule
%{_datadir}/localsearch3/extract-rules/11-iso.rule
%{_datadir}/localsearch3/extract-rules/11-msoffice-xml.rule
# libextract-gstreamer
%{_datadir}/localsearch3/extract-rules/15-gstreamer-guess.rule
%{_datadir}/localsearch3/extract-rules/15-playlist.rule
# libextract-text
%{_datadir}/localsearch3/extract-rules/15-text.rule
%{_datadir}/localsearch3/extract-rules/90-disc-generic.rule
# libextract-gstreamer
%{_datadir}/localsearch3/extract-rules/90-gstreamer-audio-generic.rule
# libextract-gstreamer
%{_datadir}/localsearch3/extract-rules/90-gstreamer-video-generic.rule
%dir %{_datadir}/localsearch3/miners
%{_datadir}/localsearch3/miners/org.freedesktop.Tracker3.Miner.Files.service
%{_mandir}/man1/localsearch-3.1*
%{_mandir}/man1/localsearch-daemon.1*
%{_mandir}/man1/localsearch-extract.1*
%{_mandir}/man1/localsearch-index.1*
%{_mandir}/man1/localsearch-info.1*
%{_mandir}/man1/localsearch-reset.1*
%{_mandir}/man1/localsearch-search.1*
%{_mandir}/man1/localsearch-status.1*
%{_mandir}/man1/localsearch-tag.1*
%{_mandir}/man1/localsearch-writeback-3.1*
%if %{with rss}
%attr(755,root,root) %{_libexecdir}/tracker-miner-rss-3
%{systemduserunitdir}/tracker-miner-rss-3.service
/etc/xdg/autostart/tracker-miner-rss-3.desktop
%{_datadir}/dbus-1/services/org.freedesktop.Tracker3.Miner.RSS.service
%{_datadir}/localsearch3/miners/org.freedesktop.Tracker3.Miner.RSS.service
%{_mandir}/man1/tracker-miner-rss-3.1*
%endif

%files testutils
%defattr(644,root,root,755)
%dir %{_libdir}/localsearch-3.0/trackertestutils
%attr(755,root,root) %{_libdir}/localsearch-3.0/trackertestutils/localsearch3-test-sandbox
%{_libdir}/localsearch-3.0/trackertestutils/*.py
