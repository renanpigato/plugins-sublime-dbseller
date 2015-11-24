Este plugin do sublime é para quem trabalha no projeto DBPlugins com o sublime, para copiar o fonte que se está editando para o projeto do dbportal sem precisar toda vez que modifica um fonte no desenvolvimento gerar o pacote do plugin e instalar no dbportal e tampouco precisar editar o fonte direto no projeto dbportal.

Copiar o fonte para o seu diretório de Plugins do sublime, normalmente em 
~/.config/sublime-text-3/Packages/User/ 

Criar os atalhos nos arquivos:
-Default (Linux).sublime-keymap
-Context.sublime-menu

Respeitando essa sintaxe 
"command": "db_plugin_copy_file", "args": {"diretorio": "***Seu diretorio do dbportal_prj, caminho absoluto ***", "useSave" : "1" }

