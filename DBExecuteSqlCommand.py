import sublime, sublime_plugin, subprocess, string, json, ast, sys, re, pprint, os
from types import *

class DbExecuteSqlCommand(sublime_plugin.TextCommand):

  def run(self, edit, **kwargs):
    
    if( kwargs != {} ):
      self.sServidor   = kwargs['servidor'];
      self.sPorta      = kwargs['porta'];
      self.sUsuario    = kwargs['usuario'];
      self.sBase       = kwargs['base'];
      self.sComando    = kwargs['comando'];
    else:
      sublime.message_dialog("String de conexão não está configurada corretamente.");
      return False;

    sArchivePath  = self.getArchivePath();
    
    sMessage = self.executaComandoShell(sArchivePath, self.sComando);
    if(sMessage == None):
      sublime.message_dialog("NÃO foi possível executar o comando.");
    else:
      self.openTerminal(sMessage);

  '''
    Define Mensagem de status da janela
  '''
  def defineStatus (self, sMensagem):
    sublime.status_message( sMensagem );

  '''
    Retorna o caminho completo até o arquivo ativo
  '''
  def getArchivePath(self):

    return str( self.view.file_name() );
    
  '''
    Retorna o caminho relativo ao ecidade para o arquivo ativo
  '''
  def getRelativePath(self, sArchivePath):

    sSearchedRelativePath = re.search('[\/].*fontes\/', sArchivePath);

    if sSearchedRelativePath == None :
      return False;
    
    sArchivePath = sArchivePath.replace(sSearchedRelativePath.group(0), '');
    return sArchivePath.replace(self.getArchiveName(), '');

  '''
    Retorna o nome do arquivo ativo
  '''
  def getArchiveName(self):

    if len(self.view.file_name()) > 0:
      filename = os.path.split(self.view.file_name())[1];
    else:
      return False;

    return filename;

  def executaComandoShell(self, sSource, sComando = 'psql'):

    try:

      sComandoShell = sComando + " -h " + self.sServidor + " -p " + self.sPorta + " -d " + self.sBase + " -U " + self.sUsuario + " -f '" + sSource + "'";
      print(sComandoShell); 
      
      if( sComando == 'cat' ):
        sComandoShell = sComando + " '" + sSource + "' | psql -h " + self.sServidor + " -p " + self.sPorta + " -d " + self.sBase + " -U " + self.sUsuario;

      output = subprocess.check_output(sComandoShell, shell = True);
      # print(output.decode('utf-8'));
      # return output.decode();
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
