{
  inputs.nixpkgs.url = "nixpkgs/nixos-23.11";

  outputs = { self, nixpkgs }:
    let
      supportedSystems =
        [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f:
        nixpkgs.lib.genAttrs supportedSystems
        (system: f { pkgs = import nixpkgs { inherit system; }; });

    in {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
            pkgs.libGLU
            pkgs.libGL
            pkgs.xorg.libX11
            pkgs.zlib
            pkgs.zstd
            pkgs.stdenv.cc.cc
            pkgs.curl
            pkgs.openssl
            pkgs.attr
            pkgs.libssh
            pkgs.bzip2
            pkgs.libxml2
            pkgs.acl
            pkgs.libsodium
            pkgs.util-linux
            pkgs.xz
            pkgs.systemd
          ];
          NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";
          shellHook = ''
            export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
          '';
          packages = let
            python3 = pkgs.python3;
            python-packages = ps:
              with ps; [
                  numpy
                  pygame
                  matplotlib
                  scipy
                  # (import ./ma-gym.nix { inherit (pkgs) lib python3Packages fetchFromGitHub; inherit pkgs python3; })
              ];
          in with pkgs; [
            (python3.withPackages python-packages)
          ];
        };
      });
    };
}
