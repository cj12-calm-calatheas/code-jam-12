{ pkgs, ... }:
{
  packages = [
    pkgs.pre-commit
  ];

  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  languages.javascript = {
    enable = true;
  };
}
