let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.11";
  gdalOverlay = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2ff53fe64443980e139eaa286017f53f88336dd0.tar.gz") {}; # pin to
  pkgs = import nixpkgs { config = {}; overlays = []; };
in pkgs.mkShell rec {
  venvDir = "./.venv";
  buildInputs = [
    pkgs.python312Packages.venvShellHook
    pkgs.python312
    gdalOverlay.python312Packages.gdal
    gdalOverlay.gdal
    pkgs.uv
    pkgs.proj
    pkgs.python312Packages.pyproj
    pkgs.nodejs_22
    pkgs.openldap
  ];

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    uv sync --all-extras
    uv run pre-commit install
  '';

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
  '';
}
