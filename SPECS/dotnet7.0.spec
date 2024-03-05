%bcond_with bootstrap

# LTO triggers a compilation error for a source level issue.  Given that LTO should not
# change the validity of any given source and the nature of the error (undefined enum), I
# suspect a generator program is mis-behaving in some way.  This needs further debugging,
# until that's done, disable LTO.  This has to happen before setting the flags below.
%define _lto_cflags %{nil}

%global host_version 7.0.16
%global runtime_version 7.0.16
%global aspnetcore_runtime_version %{runtime_version}
%global sdk_version 7.0.116
%global sdk_feature_band_version %(echo %{sdk_version} | cut -d '-' -f 1 | sed -e 's|[[:digit:]][[:digit:]]$|00|')
%global templates_version %{runtime_version}
#%%global templates_version %%(echo %%{runtime_version} | awk 'BEGIN { FS="."; OFS="." } {print $1, $2, $3+1 }')

%global host_rpm_version %{host_version}
%global runtime_rpm_version %{runtime_version}
%global aspnetcore_runtime_rpm_version %{aspnetcore_runtime_version}
%global sdk_rpm_version %{sdk_version}

# upstream can update releases without revving the SDK version so these don't always match
%global upstream_tag v%{sdk_version}

%if 0%{?fedora} || 0%{?rhel} < 8
%global use_bundled_libunwind 0
%else
%global use_bundled_libunwind 1
%endif

%ifarch aarch64 ppc64le s390x
%global use_bundled_libunwind 1
%endif

%ifarch aarch64
%global runtime_arch arm64
%endif
%ifarch ppc64le
%global runtime_arch ppc64le
%endif
%ifarch s390x
%global runtime_arch s390x
%endif
%ifarch x86_64
%global runtime_arch x64
%endif

%global mono_archs s390x ppc64le

%{!?runtime_id:%global runtime_id %(. /etc/os-release ; echo "${ID}.${VERSION_ID%%.*}")-%{runtime_arch}}

Name:           dotnet7.0
Version:        %{sdk_rpm_version}
Release:        1%{?dist}
Summary:        .NET Runtime and SDK
License:        MIT and ASL 2.0 and BSD and LGPLv2+ and CC-BY and CC0 and MS-PL and EPL-1.0 and GPL+ and GPLv2 and ISC and OFL and zlib
URL:            https://github.com/dotnet/

%if %{with bootstrap}
# The source is generated on a RHEL box via:
# ./build-dotnet-tarball --bootstrap %%{upstream_tag}
Source0:        dotnet-%{upstream_tag}-x64-bootstrap.tar.xz
# Generated via ./build-arm64-bootstrap-tarball
Source1:        dotnet-arm64-prebuilts-2022-10-12.tar.gz
# Generated manually, same pattern as the arm64 tarball
Source2:        dotnet-ppc64le-prebuilts-2022-10-21.tar.gz
# Generated manually, same pattern as the arm64 tarball
Source3:        dotnet-s390x-prebuilts-2022-10-12.tar.gz
%else
# The source is generated on a RHEL box via:
# ./build-dotnet-tarball %%{upstream_tag}
Source0:        dotnet-%{upstream_tag}.tar.gz
%endif

Source10:       check-debug-symbols.py
Source11:       dotnet.sh.in

# Disable apphost; there's no net6.0 apphost for ppc64le
Patch1:         roslyn-analyzers-ppc64le-apphost.patch
# https://github.com/dotnet/runtime/pull/95216#issuecomment-1842799314
Patch2:         runtime-re-enable-implicit-rejection.patch


%if 0%{?fedora} || 0%{?rhel} >= 8
ExclusiveArch:  aarch64 ppc64le s390x x86_64
%else
ExclusiveArch:  x86_64
%endif


BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  coreutils
%if %{without bootstrap}
BuildRequires:  dotnet-sdk-7.0
BuildRequires:  dotnet-sdk-7.0-source-built-artifacts
%endif
BuildRequires:  findutils
BuildRequires:  git
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires:  glibc-langpack-en
%endif
BuildRequires:  hostname
BuildRequires:  krb5-devel
BuildRequires:  libicu-devel
%if ! %{use_bundled_libunwind}
BuildRequires:  libunwind-devel
%endif
%ifarch aarch64
BuildRequires:  lld
%endif
# if the build ever crashes, then having lldb installed might help the
# runtime generate a backtrace for the crash
BuildRequires:  lldb
BuildRequires:  llvm
BuildRequires:  lttng-ust-devel
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  python3
BuildRequires:  tar
BuildRequires:  util-linux
BuildRequires:  zlib-devel

# Avoid generating provides and requires for private libraries
%global privlibs             libhostfxr
%global privlibs %{privlibs}|libclrgc
%global privlibs %{privlibs}|libclrjit
%global privlibs %{privlibs}|libcoreclr
%global privlibs %{privlibs}|libcoreclrtraceptprovider
%global privlibs %{privlibs}|libhostpolicy
%global privlibs %{privlibs}|libmscordaccore
%global privlibs %{privlibs}|libmscordbi
%global privlibs %{privlibs}|libnethost
%global privlibs %{privlibs}|libSystem.Globalization.Native
%global privlibs %{privlibs}|libSystem.IO.Compression.Native
%global privlibs %{privlibs}|libSystem.Native
%global privlibs %{privlibs}|libSystem.Net.Security.Native
%global privlibs %{privlibs}|libSystem.Security.Cryptography.Native.OpenSsl
%global __provides_exclude ^(%{privlibs})\\.so
%global __requires_exclude ^(%{privlibs})\\.so


%description
.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.

%if 0%{?rhel} <= 8

%package -n dotnet

Version:        %{sdk_rpm_version}
Summary:        .NET CLI tools and runtime

Requires:       dotnet-sdk-7.0%{?_isa} >= %{sdk_rpm_version}-%{release}

%description -n dotnet
.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.

%endif

%package -n dotnet-host

Version:        %{host_rpm_version}
Summary:        .NET command line launcher

%description -n dotnet-host
The .NET host is a command line program that runs a standalone
.NET application or launches the SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-hostfxr-7.0

Version:        %{host_rpm_version}
Summary:        .NET command line host resolver

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-hostfxr-7.0
The .NET host resolver contains the logic to resolve and select
the right version of the .NET SDK or runtime to use.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-runtime-7.0

Version:        %{runtime_rpm_version}
Summary:        NET 7.0 runtime

Requires:       dotnet-hostfxr-7.0%{?_isa} >= %{host_rpm_version}-%{release}

# libicu is dlopen()ed
Requires:       libicu%{?_isa}

# See src/runtime/src/libraries/Native/AnyOS/brotli-version.txt
Provides: bundled(libbrotli) = 1.0.9
%if %{use_bundled_libunwind}
# See src/runtime/src/coreclr/pal/src/libunwind/libunwind-version.txt
Provides: bundled(libunwind) = 1.5.rc1.28.g9165d2a1
%endif

%description -n dotnet-runtime-7.0
The .NET runtime contains everything needed to run .NET applications.
It includes a high performance Virtual Machine as well as the framework
libraries used by .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n aspnetcore-runtime-7.0

Version:        %{aspnetcore_runtime_rpm_version}
Summary:        ASP.NET Core 7.0 runtime

Requires:       dotnet-runtime-7.0%{?_isa} = %{runtime_rpm_version}-%{release}

%description -n aspnetcore-runtime-7.0
The ASP.NET Core runtime contains everything needed to run .NET
web applications. It includes a high performance Virtual Machine as
well as the framework libraries used by .NET applications.

ASP.NET Core is a fast, lightweight and modular platform for creating
cross platform web applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-templates-7.0

Version:        %{sdk_rpm_version}
Summary:        .NET 7.0 templates

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-templates-7.0
This package contains templates used by the .NET SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-sdk-7.0

Version:        %{sdk_rpm_version}
Summary:        .NET 7.0 Software Development Kit

Provides:       bundled(js-jquery)

Requires:       dotnet-runtime-7.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-runtime-7.0%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}

Requires:       dotnet-apphost-pack-7.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       dotnet-targeting-pack-7.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-targeting-pack-7.0%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}
Requires:       netstandard-targeting-pack-2.1%{?_isa} >= %{sdk_rpm_version}-%{release}

Requires:       dotnet-templates-7.0%{?_isa} >= %{sdk_rpm_version}-%{release}

%description -n dotnet-sdk-7.0
The .NET SDK is a collection of command line applications to
create, build, publish and run .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%global dotnet_targeting_pack() %{expand:
%package -n %{1}

Version:        %{2}
Summary:        Targeting Pack for %{3} %{4}

Requires:       dotnet-host%{?_isa}

%description -n %{1}
This package provides a targeting pack for %{3} %{4}
that allows developers to compile against and target %{3} %{4}
applications using the .NET SDK.

%files -n %{1}
%dir %{_libdir}/dotnet/packs
%{_libdir}/dotnet/packs/%{5}
}

%dotnet_targeting_pack dotnet-apphost-pack-7.0 %{runtime_rpm_version} Microsoft.NETCore.App 7.0 Microsoft.NETCore.App.Host.%{runtime_id}
%dotnet_targeting_pack dotnet-targeting-pack-7.0 %{runtime_rpm_version} Microsoft.NETCore.App 7.0 Microsoft.NETCore.App.Ref
%dotnet_targeting_pack aspnetcore-targeting-pack-7.0 %{aspnetcore_runtime_rpm_version} Microsoft.AspNetCore.App 7.0 Microsoft.AspNetCore.App.Ref
#%%dotnet_targeting_pack netstandard-targeting-pack-2.1 %%{sdk_rpm_version} NETStandard.Library 2.1 NETStandard.Library.Ref


%package -n dotnet-sdk-7.0-source-built-artifacts

Version:        %{sdk_rpm_version}
Summary:        Internal package for building .NET 7.0 Software Development Kit

%description -n dotnet-sdk-7.0-source-built-artifacts
The .NET source-built archive is a collection of packages needed
to build the .NET SDK itself.

These are not meant for general use.


%prep
%if %{without bootstrap}
%setup -q -n dotnet-%{upstream_tag}

# Remove all prebuilts
find -iname '*.dll' -type f -delete
find -iname '*.so' -type f -delete
find -iname '*.tar.gz' -type f -delete
find -iname '*.nupkg' -type f -delete
find -iname '*.zip' -type f -delete

rm -rf .dotnet/
rm -rf packages/source-built

mkdir -p packages/archive
ln -s %{_libdir}/dotnet/source-built-artifacts/Private.SourceBuilt.Artifacts.*.tar.gz packages/archive/

%else

%setup -q -T -b 0 -n dotnet-%{upstream_tag}-x64-bootstrap

%ifnarch x86_64

rm -rf .dotnet
%ifarch aarch64
tar -x --strip-components=1 -f %{SOURCE1} -C packages/prebuilt
%endif
%ifarch ppc64le
tar -x --strip-components=1 -f %{SOURCE2} -C packages/prebuilt
%endif
%ifarch s390x
tar -x --strip-components=1 -f %{SOURCE3} -C packages/prebuilt
%endif

mkdir -p .dotnet
tar xf packages/prebuilt/dotnet-sdk*.tar.gz -C .dotnet/
rm packages/prebuilt/dotnet-sdk*.tar.gz

boot_sdk_version=$(ls -1 .dotnet/sdk/)
sed -i -E 's|"dotnet": "[^"]+"|"dotnet" : "'$boot_sdk_version'"|' global.json

%ifarch ppc64le s390x
ilasm_version=$(ls packages/prebuilt| grep -i ilasm | tr 'A-Z' 'a-z' | sed -E 's|runtime.linux-'%{runtime_arch}'.microsoft.netcore.ilasm.||' | sed -E 's|.nupkg$||')
echo $ilasm_version

mkdir -p packages-customized-local
pushd packages-customized-local
tar xf ../packages/archive/Private.SourceBuilt.Artifacts.*.tar.gz
sed -i -E 's|<MicrosoftNETCoreILAsmVersion>[^<]+</MicrosoftNETCoreILAsmVersion>|<MicrosoftNETCoreILAsmVersion>'$ilasm_version'</MicrosoftNETCoreILAsmVersion>|' PackageVersions.props
sed -i -E 's|<MicrosoftNETCoreILDAsmVersion>[^<]+</MicrosoftNETCoreILDAsmVersion>|<MicrosoftNETCoreILDAsmVersion>'$ilasm_version'</MicrosoftNETCoreILDAsmVersion>|' PackageVersions.props
tar czf ../packages/archive/Private.SourceBuilt.Artifacts.*.tar.gz *
popd

%endif

%endif

%endif

%patch1 -p1
%patch2 -p1

# Fix bad hardcoded path in build
sed -i 's|/usr/share/dotnet|%{_libdir}/dotnet|' src/runtime/src/native/corehost/hostmisc/pal.unix.cpp

%if ! %{use_bundled_libunwind}
sed -i -E 's|( /p:BuildDebPackage=false)|\1 --cmakeargs -DCLR_CMAKE_USE_SYSTEM_LIBUNWIND=TRUE|' src/runtime/eng/SourceBuild.props
%endif


%build
cat /etc/os-release

%if %{without bootstrap}
# We need to create a copy because we will mutate this
cp -a %{_libdir}/dotnet previously-built-dotnet
find previously-built-dotnet
%endif

%if 0%{?fedora} || 0%{?rhel} >= 9
# Setting this macro ensures that only clang supported options will be
# added to ldflags and cflags.
%global toolchain clang
%set_build_flags
%else
# Filter flags not supported by clang
%global dotnet_cflags %(echo %optflags | sed -re 's/-specs=[^ ]*//g')
%global dotnet_ldflags %(echo %{__global_ldflags} | sed -re 's/-specs=[^ ]*//g')
export CFLAGS="%{dotnet_cflags}"
export CXXFLAGS="%{dotnet_cflags}"
export LDFLAGS="%{dotnet_ldflags}"
%endif

# -fstack-clash-protection breaks CoreCLR
CFLAGS=$(echo $CFLAGS  | sed -e 's/-fstack-clash-protection//' )
CXXFLAGS=$(echo $CXXFLAGS  | sed -e 's/-fstack-clash-protection//' )

%ifarch aarch64
# -mbranch-protection=standard breaks unwinding in CoreCLR through libunwind
CFLAGS=$(echo $CFLAGS | sed -e 's/-mbranch-protection=standard //')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/-mbranch-protection=standard //')
%endif

%ifarch s390x
# -march=z13 -mtune=z14 makes clang crash while compiling .NET
CFLAGS=$(echo $CFLAGS | sed -e 's/ -march=z13//')
CFLAGS=$(echo $CFLAGS | sed -e 's/ -mtune=z14//')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/ -march=z13//')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/ -mtune=z14//')
%endif

export EXTRA_CFLAGS="$CFLAGS"
export EXTRA_CXXFLAGS="$CXXFLAGS"
export EXTRA_LDFLAGS="$LDFLAGS"

# Disable tracing, which is incompatible with certain versions of
# lttng See https://github.com/dotnet/runtime/issues/57784. The
# suggested compile-time change doesn't work, unfortunately.
export COMPlus_LTTng=0

%if 0%{?rhel} >= 9
# OpenSSL 3.0 in RHEL 9 has disabled SHA1, used by .NET for strong
# name signing. See https://github.com/dotnet/runtime/issues/67304
# https://gitlab.com/redhat/centos-stream/rpms/openssl/-/commit/78fb78d30755ae18fdaef28ef392f4e67c662ff6
export OPENSSL_ENABLE_SHA1_SIGNATURES=1
%endif

VERBOSE=1 ./build.sh \
%if %{without bootstrap}
    --with-sdk previously-built-dotnet \
%endif
%ifarch %{mono_archs}
    --use-mono-runtime \
%endif
    -- \
    /p:MinimalConsoleLogOutput=false \
    /p:ContinueOnPrebuiltBaselineError=true \
    /v:n \
    /p:LogVerbosity=n \


echo \
    /p:SkipPortableRuntimeBuild=true \


sed -e 's|[@]LIBDIR[@]|%{_libdir}|g' %{SOURCE11} > dotnet.sh


%install
install -dm 0755 %{buildroot}%{_libdir}/dotnet
ls artifacts/%{runtime_arch}/Release
tar xf artifacts/%{runtime_arch}/Release/dotnet-sdk-%{sdk_version}-%{runtime_id}.tar.gz -C %{buildroot}%{_libdir}/dotnet/

# See https://github.com/dotnet/source-build/issues/2579
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'testhost.x86' -delete
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'vstest.console' -delete

# Install managed symbols: disabled because they don't contain sources
# but point to the paths the sources would have been at in the build
# servers. The end user experience is pretty bad atm.
# tar xf artifacts/%%{runtime_arch}/Release/runtime/dotnet-runtime-symbols-%%{runtime_id}-%%{runtime_version}.tar.gz \
#    -C %%{buildroot}/%%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%%{runtime_version}/

# Fix executable permissions on files
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'apphost' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'singlefilehost' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name 'lib*so' -exec chmod +x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.a' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.dll' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.h' -exec chmod 0644 {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.json' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pdb' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.props' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pubxml' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.targets' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.txt' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.xml' -exec chmod -x {} \;

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_sysconfdir}/profile.d/
#install dotnet.sh %%{buildroot}%%{_sysconfdir}/profile.d/

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}/%%{_datadir}/bash-completion/completions
# dynamic completion needs the file to be named the same as the base command
#install src/sdk/scripts/register-completions.bash %%{buildroot}/%%{_datadir}/bash-completion/completions/dotnet

# TODO: the zsh completion script needs to be ported to use #compdef
#install -dm 755 %%{buildroot}/%%{_datadir}/zsh/site-functions
#install src/cli/scripts/register-completions.zsh %%{buildroot}/%%{_datadir}/zsh/site-functions/_dotnet

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_bindir}
#ln -s ../../%%{_libdir}/dotnet/dotnet %%{buildroot}%%{_bindir}/

# Provided by dotnet-host from another SRPM
#for section in 1 7; do
#    install -dm 0755 %%{buildroot}%%{_mandir}/man${section}/
#    find -iname 'dotnet*'.${section} -type f -exec cp {} %%{buildroot}%%{_mandir}/man${section}/ \;
#done

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_sysconfdir}/dotnet
#echo "%%{_libdir}/dotnet" >> install_location
#install install_location %%{buildroot}%%{_sysconfdir}/dotnet/
#echo "%%{_libdir}/dotnet" >> install_location_%%{runtime_arch}
#install install_location_%%{runtime_arch} %%{buildroot}%%{_sysconfdir}/dotnet/

install -dm 0755 %{buildroot}%{_libdir}/dotnet/source-built-artifacts
install -m 0644 artifacts/%{runtime_arch}/Release/Private.SourceBuilt.Artifacts.*.tar.gz %{buildroot}/%{_libdir}/dotnet/source-built-artifacts/


# Quick and dirty check for https://github.com/dotnet/source-build/issues/2731
test -f %{buildroot}%{_libdir}/dotnet/sdk/%{sdk_version}/Sdks/Microsoft.NET.Sdk/Sdk/Sdk.props

# Check debug symbols in all elf objects. This is not in %%check
# because native binaries are stripped by rpm-build after %%install.
# So we need to do this check earlier.
echo "Testing build results for debug symbols..."
%{SOURCE10} -v %{buildroot}%{_libdir}/dotnet/


# Self-check
%if 0%{?fedora} > 35
# lttng in Fedora > 35 is incompatible with .NET
export COMPlus_LTTng=0
%endif

%{buildroot}%{_libdir}/dotnet/dotnet --info
%{buildroot}%{_libdir}/dotnet/dotnet --version

# Provided by dotnet-host from another SRPM
rm %{buildroot}%{_libdir}/dotnet/LICENSE.txt
rm %{buildroot}%{_libdir}/dotnet/ThirdPartyNotices.txt
rm %{buildroot}%{_libdir}/dotnet/dotnet

# Provided by netstandard-targeting-pack-2.1 from another SRPM
rm -rf %{buildroot}%{_libdir}/dotnet/packs/NETStandard.Library.Ref/2.1.0


%files -n dotnet-hostfxr-7.0
%dir %{_libdir}/dotnet/host/fxr
%{_libdir}/dotnet/host/fxr/%{host_version}

%files -n dotnet-runtime-7.0
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.NETCore.App
%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%{runtime_version}

%files -n aspnetcore-runtime-7.0
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.AspNetCore.App
%{_libdir}/dotnet/shared/Microsoft.AspNetCore.App/%{aspnetcore_runtime_version}

%files -n dotnet-templates-7.0
%dir %{_libdir}/dotnet/templates
%{_libdir}/dotnet/templates/%{templates_version}

%files -n dotnet-sdk-7.0
%dir %{_libdir}/dotnet/sdk
%{_libdir}/dotnet/sdk/%{sdk_version}
%dir %{_libdir}/dotnet/sdk-manifests
%{_libdir}/dotnet/sdk-manifests/%{sdk_feature_band_version}
%{_libdir}/dotnet/metadata
%dir %{_libdir}/dotnet/packs

%files -n dotnet-sdk-7.0-source-built-artifacts
%dir %{_libdir}/dotnet
%{_libdir}/dotnet/source-built-artifacts


%changelog
* Thu Feb 01 2024 Omair Majid <omajid@redhat.com> - 7.0.116-1
- Update to .NET SDK 7.0.116 and Runtime 7.0.16
- Resolves: RHEL-23793

* Wed Dec 20 2023 Omair Majid <omajid@redhat.com> - 7.0.115-1
- Update to .NET SDK 7.0.115 and Runtime 7.0.15
- Resolves: RHEL-19808

* Thu Nov 02 2023 Omair Majid <omajid@redhat.com> - 7.0.114-1
- Update to .NET SDK 7.0.114 and Runtime 7.0.14
- Resolves: RHEL-15357

* Tue Oct 24 2023 Omair Majid <omajid@redhat.com> - 7.0.113-2
- Update to .NET SDK 7.0.113 and Runtime 7.0.13
- Resolves: RHEL-14467

* Mon Oct 16 2023 Omair Majid <omajid@redhat.com> - 7.0.112-2
- Update to .NET SDK 7.0.112 and Runtime 7.0.12
- Resolves: RHEL-11698

* Tue Sep 12 2023 Omair Majid <omajid@redhat.com> - 7.0.111-2
- Update to .NET SDK 7.0.111 and Runtime 7.0.11
- Resolves: RHEL-2000

* Wed Aug 09 2023 Omair Majid <omajid@redhat.com> - 7.0.110-2
- Update to .NET SDK 7.0.110 and Runtime 7.0.10
- Resolves: RHBZ#2228571

* Tue Jul 11 2023 Omair Majid <omajid@redhat.com> - 7.0.109-2
- Update to .NET SDK 7.0.109 and Runtime 7.0.9
- Resolves: RHBZ#2219632

* Tue Jun 13 2023 Andrew Slice <andrew.slice@redhat.com> - 7.0.107-2
- Update to .NET SDK 7.0.107 and Runtime 7.0.7
- Resolves: RHBZ#2211767

* Wed Apr 12 2023 Omair Majid <omajid@redhat.com> - 7.0.105-2
- Update to .NET SDK 7.0.105 and Runtime 7.0.5
- Resolves: RHBZ#2183591

* Tue Mar 28 2023 Omair Majid <omajid@redhat.com> - 7.0.104-2
- Bump Release
- Related: RHBZ#2175025

* Mon Mar 20 2023 Omair Majid <omajid@redhat.com> - 7.0.104-1
- Update to .NET SDK 7.0.104 and Runtime 7.0.4
- Resolves: RHBZ#2175025

* Fri Mar 10 2023 Omair Majid <omajid@redhat.com> - 7.0.103-1
- Update to .NET SDK 7.0.103 and Runtime 7.0.3
- Resolves: RHBZ#2166773

* Thu Mar 09 2023 Omair Majid <omajid@redhat.com> - 7.0.102-1
- Update to .NET SDK 7.0.102 and Runtime 7.0.2
- Resolves: RHBZ#2154465

* Wed Jan 11 2023 Omair Majid <omajid@redhat.com> - 7.0.101-2
- Update to .NET SDK 7.0.101 and Runtime 7.0.1
- Resolves: RHBZ#2150150

* Wed Nov 09 2022 Omair Majid <omajid@redhat.com> - 7.0.100-1
- Update to .NET 7 GA release
- Resolves: RHBZ#2137944

* Tue Oct 25 2022 Omair Majid <omajid@redhat.com> - 7.0.100-0.5.rc2
- Add lldb as a build dependency
- Related: RHBZ#2134641

* Mon Oct 24 2022 Omair Majid <omajid@redhat.com> - 7.0.100-0.4.rc2
- Enable ppc64le builds
- Related: RHBZ#2134641

* Thu Oct 13 2022 Omair Majid <omajid@redhat.com> - 7.0.100-0.3.rc2
- Update to .NET 7 RC 2
- Resolves: RHBZ#2134641

* Sat Sep 17 2022 Omair Majid <omajid@redhat.com> - 7.0.100-0.2.rc1
- Update to .NET 7 RC 1
- Enable s390x builds
- Resolves: RHBZ#2123884

* Thu Aug 25 2022 Omair Majid <omajid@redhat.com> - 7.0.100-0.1
- Initial .NET 7 package
- Resolves: RHBZ#2112027

* Wed May 11 2022 Omair Majid <omajid@redhat.com> - 6.0.105-1
- Update to .NET SDK 6.0.105 and Runtime 6.0.5

* Tue Apr 12 2022 Omair Majid <omajid@redhat.com> - 6.0.104-1
- Update to .NET SDK 6.0.104 and Runtime 6.0.4

* Thu Mar 10 2022 Omair Majid <omajid@redhat.com> - 6.0.103-1
- Update to .NET SDK 6.0.103 and Runtime 6.0.3

* Mon Feb 14 2022 Omair Majid <omajid@redhat.com> - 6.0.102-1
- Update to .NET SDK 6.0.102 and Runtime 6.0.2

* Fri Jan 28 2022 Omair Majid <omajid@redhat.com> - 6.0.101-3
- Update to .NET SDK 6.0.101 and Runtime 6.0.1

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.100-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Dec 20 2021 Omair Majid <omajid@redhat.com> - 6.0.100-2
- Disable bootstrap

* Sun Dec 19 2021 Omair Majid <omajid@redhat.com> - 6.0.100-1
- Update to .NET 6

* Fri Oct 22 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.7.rc2
- Update to .NET 6 RC2

* Fri Oct 08 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.6.28be3e9a006d90d8c6e87d4353b77882829df718
- Enable building on arm64
- Related: RHBZ#1986017

* Sun Oct 03 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.5.28be3e9a006d90d8c6e87d4353b77882829df718
- Enable building on s390x
- Related: RHBZ#1986017

* Sun Oct 03 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.4.28be3e9a006d90d8c6e87d4353b77882829df718
- Clean up tarball and add initial support for s390x
- Related: RHBZ#1986017

* Sun Sep 26 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.3.28be3e9a006d90d8c6e87d4353b77882829df718
- Update to work-in-progress RC2 release

* Wed Aug 25 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.2.preview6
- Updated to build the latest source-build preview

* Fri Jul 23 2021 Omair Majid <omajid@redhat.com> - 6.0.0-0.1.preview6
- Initial package for .NET 6

* Thu Jun 10 2021 Omair Majid <omajid@redhat.com> - 5.0.204-1
- Update to .NET SDK 5.0.204 and Runtime 5.0.7

* Wed May 12 2021 Omair Majid <omajid@redhat.com> - 5.0.203-1
- Update to .NET SDK 5.0.203 and Runtime 5.0.6

* Wed Apr 14 2021 Omair Majid <omajid@redhat.com> - 5.0.202-1
- Update to .NET SDK 5.0.202 and Runtime 5.0.5

* Tue Apr 06 2021 Omair Majid <omajid@redhat.com> - 5.0.104-2
- Mark files under /etc/ as config(noreplace)
- Add an rpm-inspect configuration file
- Add an rpmlintrc file
- Enable gating for release branches and ELN too

* Tue Mar 16 2021 Omair Majid <omajid@redhat.com> - 5.0.104-1
- Update to .NET SDK 5.0.104 and Runtime 5.0.4
- Drop unneeded/upstreamed patches

* Wed Feb 17 2021 Omair Majid <omajid@redhat.com> - 5.0.103-2
- Add Fedora 35 RIDs

* Thu Feb 11 2021 Omair Majid <omajid@redhat.com> - 5.0.103-1
- Update to .NET SDK 5.0.103 and Runtime 5.0.3

* Fri Jan 29 2021 Omair Majid <omajid@redhat.com> - 5.0.102-2
- Disable bootstrap

* Fri Dec 18 2020 Omair Majid <omajid@redhat.com> - 5.0.100-2
- Update to .NET Core Runtime 5.0.0 and SDK 5.0.100 commit 9c4e5de

* Fri Dec 04 2020 Omair Majid <omajid@redhat.com> - 5.0.100-1
- Update to .NET Core Runtime 5.0.0 and SDK 5.0.100

* Thu Dec 03 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.4.20201202git337413b
- Update to latest 5.0 pre-GA commit

* Tue Nov 24 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.4.20201123gitdee899c
- Update to 5.0 pre-GA commit

* Mon Sep 14 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.3.preview8
- Update to Preview 8

* Fri Jul 10 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.2.preview4
- Fix building with custom CFLAGS/CXXFLAGS/LDFLAGS
- Clean up patches

* Mon Jul 06 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.1.preview4
- Initial build

* Sat Jun 27 2020 Omair Majid <omajid@redhat.com> - 3.1.105-4
- Disable bootstrap

* Fri Jun 26 2020 Omair Majid <omajid@redhat.com> - 3.1.105-3
- Re-bootstrap aarch64

* Fri Jun 19 2020 Omair Majid <omajid@redhat.com> - 3.1.105-3
- Disable bootstrap

* Thu Jun 18 2020 Omair Majid <omajid@redhat.com> - 3.1.105-1
- Bootstrap aarch64

* Tue Jun 16 2020 Chris Rummel <crummel@microsoft.com> - 3.1.105-1
- Update to .NET Core Runtime 3.1.5 and SDK 3.1.105

* Fri Jun 05 2020 Chris Rummel <crummel@microsoft.com> - 3.1.104-1
- Update to .NET Core Runtime 3.1.4 and SDK 3.1.104

* Thu Apr 09 2020 Chris Rummel <crummel@microsoft.com> - 3.1.103-1
- Update to .NET Core Runtime 3.1.3 and SDK 3.1.103

* Mon Mar 16 2020 Omair Majid <omajid@redhat.com> - 3.1.102-1
- Update to .NET Core Runtime 3.1.2 and SDK 3.1.102

* Fri Feb 28 2020 Omair Majid <omajid@redhat.com> - 3.1.101-4
- Disable bootstrap

* Fri Feb 28 2020 Omair Majid <omajid@redhat.com> - 3.1.101-3
- Enable bootstrap
- Add Fedora 33 runtime ids

* Thu Feb 27 2020 Omair Majid <omajid@redhat.com> - 3.1.101-2
- Disable bootstrap

* Tue Jan 21 2020 Omair Majid <omajid@redhat.com> - 3.1.101-1
- Update to .NET Core Runtime 3.1.1 and SDK 3.1.101

* Thu Dec 05 2019 Omair Majid <omajid@redhat.com> - 3.1.100-1
- Update to .NET Core Runtime 3.1.0 and SDK 3.1.100

* Mon Nov 18 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.4.preview3
- Fix apphost permissions

* Fri Nov 15 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.3.preview3
- Update to .NET Core Runtime 3.1.0-preview3.19553.2 and SDK
  3.1.100-preview3-014645

* Wed Nov 06 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.2
- Update to .NET Core 3.1 Preview 2

* Wed Oct 30 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.1
- Update to .NET Core 3.1 Preview 1

* Thu Oct 24 2019 Omair Majid <omajid@redhat.com> - 3.0.100-5
- Add cgroupv2 support to .NET Core

* Wed Oct 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-4
- Include fix from coreclr for building on Fedora 32

* Wed Oct 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-3
- Harden built binaries to pass annocheck

* Fri Oct 11 2019 Omair Majid <omajid@redhat.com> - 3.0.100-2
- Export DOTNET_ROOT in profile to make apphost lookup work

* Fri Sep 27 2019 Omair Majid <omajid@redhat.com> - 3.0.100-1
- Update to .NET Core Runtime 3.0.0 and SDK 3.0.100

* Wed Sep 25 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.18.rc1
- Update to .NET Core Runtime 3.0.0-rc1-19456-20 and SDK 3.0.100-rc1-014190

* Tue Sep 17 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.16.preview9
- Fix files duplicated between dotnet-apphost-pack-3.0 and dotnet-targeting-pack-3.0
- Fix dependencies between .NET SDK and the targeting packs

* Mon Sep 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.15.preview9
- Update to .NET Core Runtime 3.0.0-preview 9 and SDK 3.0.100-preview9

* Mon Aug 19 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.11.preview8
- Update to .NET Core Runtime 3.0.0-preview8-28405-07 and SDK
  3.0.100-preview8-013656

* Tue Jul 30 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.9.preview7
- Update to .NET Core Runtime 3.0.0-preview7-27912-14 and SDK
  3.0.100-preview7-012821

* Fri Jul 26 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.8.preview7
- Update to .NET Core Runtime 3.0.0-preview7-27902-19 and SDK
  3.0.100-preview7-012802

* Wed Jun 26 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.7.preview6
- Obsolete dotnet-sdk-3.0.1xx
- Add supackages for targeting packs
- Add -fcf-protection to CFLAGS

* Wed Jun 26 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.6.preview6
- Update to .NET Core Runtime 3.0.0-preview6-27804-01 and SDK 3.0.100-preview6-012264
- Set dotnet installation location in /etc/dotnet/install_location
- Update targeting packs
- Install managed symbols
- Completely conditionalize libunwind bundling

* Tue May 07 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.3.preview4
- Update to .NET Core 3.0 preview 4

* Tue Dec 18 2018 Omair Majid <omajid@redhat.com> - 3.0.0-0.1.preview1
- Update to .NET Core 3.0 preview 1

* Fri Dec 07 2018 Omair Majid <omajid@redhat.com> - 2.2.100
- Update to .NET Core 2.2.0

* Wed Nov 07 2018 Omair Majid <omajid@redhat.com> - 2.2.100-0.2.preview3
- Update to .NET Core 2.2.0-preview3

* Fri Nov 02 2018 Omair Majid <omajid@redhat.com> - 2.1.403-3
- Add host-fxr-2.1 subpackage

* Mon Oct 15 2018 Omair Majid <omajid@redhat.com> - 2.1.403-2
- Disable telemetry by default
- Users have to manually export DOTNET_CLI_TELEMETRY_OPTOUT=0 to enable

* Tue Oct 02 2018 Omair Majid <omajid@redhat.com> - 2.1.403-1
- Update to .NET Core Runtime 2.1.5 and SDK 2.1.403

* Wed Sep 26 2018 Omair Majid <omajid@redhat.com> - 2.1.402-2
- Add ~/.dotnet/tools to $PATH to make it easier to use dotnet tools

* Thu Sep 13 2018 Omair Majid <omajid@redhat.com> - 2.1.402-1
- Update to .NET Core Runtime 2.1.4 and SDK 2.1.402

* Wed Sep 05 2018 Omair Majid <omajid@redhat.com> - 2.1.401-2
- Use distro-standard flags when building .NET Core

* Tue Aug 21 2018 Omair Majid <omajid@redhat.com> - 2.1.401-1
- Update to .NET Core Runtime 2.1.3 and SDK 2.1.401

* Mon Aug 20 2018 Omair Majid <omajid@redhat.com> - 2.1.302-1
- Update to .NET Core Runtime 2.1.2 and SDK 2.1.302

* Fri Jul 20 2018 Omair Majid <omajid@redhat.com> - 2.1.301-1
- Update to .NET Core 2.1

* Thu May 03 2018 Omair Majid <omajid@redhat.com> - 2.0.7-1
- Update to .NET Core 2.0.7

* Wed Mar 28 2018 Omair Majid <omajid@redhat.com> - 2.0.6-2
- Enable bash completion for dotnet
- Remove redundant buildrequires and requires

* Wed Mar 14 2018 Omair Majid <omajid@redhat.com> - 2.0.6-1
- Update to .NET Core 2.0.6

* Fri Feb 23 2018 Omair Majid <omajid@redhat.com> - 2.0.5-1
- Update to .NET Core 2.0.5

* Wed Jan 24 2018 Omair Majid <omajid@redhat.com> - 2.0.3-5
- Don't apply corefx clang warnings fix on clang < 5

* Fri Jan 19 2018 Omair Majid <omajid@redhat.com> - 2.0.3-4
- Add a test script to sanity check debug and symbol info.
- Build with clang 5.0
- Make main package real instead of using a virtual provides (see RHBZ 1519325)

* Wed Nov 29 2017 Omair Majid <omajid@redhat.com> - 2.0.3-3
- Add a Provides for 'dotnet'
- Fix conditional macro

* Tue Nov 28 2017 Omair Majid <omajid@redhat.com> - 2.0.3-2
- Fix build on Fedora 27

* Fri Nov 17 2017 Omair Majid <omajid@redhat.com> - 2.0.3-1
- Update to .NET Core 2.0.3

* Thu Oct 19 2017 Omair Majid <omajid@redhat.com> - 2.0.0-4
- Add a hack to let omnisharp work

* Wed Aug 30 2017 Omair Majid <omajid@redhat.com> - 2.0.0-3
- Add a patch for building coreclr and core-setup correctly on Fedora >= 27

* Fri Aug 25 2017 Omair Majid <omajid@redhat.com> - 2.0.0-2
- Move libicu/libcurl/libunwind requires to runtime package
- Make sdk depend on the exact version of the runtime package

* Thu Aug 24 2017 Omair Majid <omajid@redhat.com> - 2.0.0-1
- Update to 2.0.0 final release

* Wed Jul 26 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.3.preview2
- Add man pages

* Tue Jul 25 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.2.preview2
- Add Requires on libicu
- Split into multiple packages
- Do not repeat first-run message

* Fri Jul 21 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.1.preview2
- Update to .NET Core 2.0 Preview 2

* Thu Mar 16 2017 Nemanja Milošević <nmilosevnm@gmail.com> - 1.1.0-7
- rebuilt with latest libldb
* Wed Feb 22 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-6
- compat-openssl 1.0 for F26 for now
* Sun Feb 19 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-5
- Fix wrong commit id's
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-4
- Use commit id's instead of branch names
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-3
- Improper patch5 fix
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-2
- SPEC cleanup
- git removal (using all tarballs for reproducible builds)
- more reasonable versioning
* Thu Feb 09 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-1
- Fixed debuginfo going to separate package (Patch1)
- Added F25/F26 RIL and fixed the version info (Patch2)
- Added F25/F26 RIL in Microsoft.NETCore.App suported runtime graph (Patch3)
- SPEC file cleanup
* Wed Jan 11 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-0
- Initial RPM for Fedora 25/26.
