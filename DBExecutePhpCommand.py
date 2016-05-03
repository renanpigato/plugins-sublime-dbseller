import sublime, sublime_plugin, subprocess, string, json, ast, sys, re, pprint, os
from types import *

class DbExecutePhpCommand(sublime_plugin.TextCommand):

  def run(self, edit, **kwargs):
    
    if( kwargs != {} ):
      self.sComando    = kwargs['comando'];
      self.sPathToExec = kwargs['path'];
      self.sSource     = kwargs['source'];
      self.sArgs       = kwargs['args'];
    else:
      sublime.message_dialog("Comando não está configurado corretamente.");
      return False;

    sArchive  = self.sSource;
    if(self.sSource == None):
      sArchive  = self.getArchiveName();

    sArgs = self.sArgs;
    if(self.sArgs == None):
      sArgs = '';
    
    sMessage = self.executaComandoShell(sArchive, self.sComando, sArgs);
    if(sMessage == None):
      sublime.message_dialog("NÃO foi possível executar o comando.");
    else:
      self.openTerminal(sMessage);

  '''
    Retorna o caminho completo até o arquivo ativo
  '''
  def getArchivePath(self):

    return str( self.view.file_name() );

  '''
    Retorna o nome do arquivo ativo
  '''
  def getArchiveName(self):
    
    sArchivePath = self.getArchivePath();
    if len(sArchivePath) > 0:
      print(os.path.split(sArchivePath));
      filename = os.path.split(sArchivePath)[1];
    else:
      return False;

    return filename;

  '''
    Retorna o caminho relativo ao ecidade para o arquivo ativo
  '''
  def getRelativePath(self, sArchivePath):

    sSearchedProject      = re.search('.*?\/', sArchivePath.split('/var/www/')[1]);

    if sSearchedProject == None :
      return False;
    
    sSearchedProject      = sSearchedProject.group(0).replace("/", "");
    sSearchedRelativePath = "/var/www/" + sSearchedProject;
    return sSearchedRelativePath;
  
  '''
    Executa o comando no shel
  '''  
  def executaComandoShell(self, sSource, sComando = 'php', sArgs = '' ):

    try:

      sComandoShell = "cd " + self.sPathToExec + " && " + sComando + " '" + sSource + "' " + sArgs;
      output = subprocess.check_output(sComandoShell, shell = True);

      print(sComandoShell);
      print(output);
      
      return output.decode('utf8');

    except:
      self.openTerminal("Erro ao executar o comando ---> " + sComandoShell);

  '''
    Abre a janela do terminal com saida do console
  '''
  def openTerminal(self, sSaida):

    self.output_view = self.view.window().create_output_panel("textarea");
    window = sublime.active_window();
    window.run_command("show_panel", {"panel": "output.textarea"});
    self.output_view.set_read_only(False);
    self.output_view.run_command("append", {"characters": sSaida});
