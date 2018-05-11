with import<nixpkgs> {};
stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = [
  python3
  python36Packages.pip
  python36Packages.flask
  python36Packages.virtualenv
  ];
}
