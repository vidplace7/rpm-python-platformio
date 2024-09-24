%global forgeurl https://github.com/platformio/platformio-core
%global pypi_name platformio
%global srcname platformio-core

# Tests require Internet access
%bcond_with tests

Name:           python-%{pypi_name}
Version:        6.1.14
Release:        %autorelease
Summary:        Professional collaborative platform for embedded development

License:        Apache-2.0
URL:            https://platformio.org
# PyPI is missing tests, so use the GitHub tarball instead
Source:         %{forgeurl}/archive/v%{version}/%{srcname}-%{version}.tar.gz
# Update 99-platformio-udev.rules
Patch0:         %{forgeurl}/commit/2bad42ecb1271a52203f585b970e13466c2cddb1.patch
# Fedora: disable telemetry by default
Patch1:         platformio-default-telemetry-off.patch
# Fedora: neuter update logic for platformio itself
Patch2:         platformio-short-circuit-upgrades.patch
# Allow Starlette 0.38.1 (#4953)
# https://github.com/platformio/platformio-core/commit/9eb6e5166d4a7c366e5cacbd39fc467c16644667
# Allow Starlette 0.39.x
# https://github.com/platformio/platformio-core/commit/4b61de01369e1a943cf1c93564d189ec66580fbd
# Cherry-picked to v6.1.14.
Patch3:         platformio-starlette-0.39.patch
# Update bottle to 0.13.*
# https://github.com/platformio/platformio-core/commit/4230b223d2cf307408fdd4b1e077f0b149221f13
# Cherry-picked to v6.1.14.
# For Fedora 42 and later.
Patch100:       0001-Update-bottle-to-0.13.patch

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros

%global _description %{expand:
PlatformIO is a cross-platform, cross-architecture, multiple framework,
professional tool for embedded systems engineers and for software developers
who write applications for embedded products.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description

%package -n     %{pypi_name}
Summary:        %{summary}
Requires:       python3-%{pypi_name} = %{version}-%{release}
Requires:       systemd-udev

%description -n %{pypi_name} %_description

This package contains the PlatformIO command-line utilites and udev rules.

%prep
%autosetup -p1 -n %{srcname}-%{version} -N
%autopatch -M99 -p1
%if !0%{?fc39} && !0%{?fc40} && !0%{?fc41}
%patch 100 -p1
%endif

%generate_buildrequires
%pyproject_buildrequires -t

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

# Replace duplicate binary with symlink
ln -sf platformio %{buildroot}%{_bindir}/pio

# Install udev rules
mkdir -p %{buildroot}%{_udevrulesdir}
ln -s %{python3_sitelib}/%{pypi_name}/assets/system/99-platformio-udev.rules \
  %{buildroot}%{_udevrulesdir}/

%check
%if %{with tests}
%tox -e testcore
%else
# Exclude modules that require platformio-managed dependencies
%pyproject_check_import -e 'platformio.builder.*' -e 'platformio.remote.*'
%endif

%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.rst HISTORY.rst

%files -n %{pypi_name}
%{_bindir}/pio
%{_bindir}/piodebuggdb
%{_bindir}/platformio
%{_udevrulesdir}/99-platformio-udev.rules

%changelog
%autochangelog
