import sublime, sublime_plugin, subprocess, string, json, ast, sys, re, pprint, os
from types import *

class DbPluginCopyFileCommand(sublime_plugin.TextCommand):

  def run(self, edit, **kwargs):

    if( kwargs != {} ):
      sPathToDbportal = kwargs['diretorio'];
      sPathToDbportal = sPathToDbportal +"/";
      lUseSave        = kwargs['useSave'];
    else:
      sublime.message_dialog("O diretório do E-cidade não está configurado.");
      return False;

    sArchivePath  = self.getArchivePath(); 
    sRelativePath = self.getRelativePath(sArchivePath);
    
    if( lUseSave == "1" ):
      self.view.run_command('save');
    
    if( sRelativePath != False ):
      if(self.executaComandoCopyShell(sArchivePath, sPathToDbportal + sRelativePath) == None):
        sublime.message_dialog("NÃO foi possível executar o comando.");
      else:
        self.defineStatus("Arquivo: "+  self.getArchiveName() +" Copiado com sucesso para: "+ sPathToDbportal + sRelativePath);

    else:
      sublime.message_dialog("Não foi possível recuperar o caminho relativo ao ecidade");

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

  def executaComandoCopyShell(self, sSourcePath, sDestinationPath, sComando = 'cp'):

    try:

      if( sSourcePath == '' ):
        sublime.message_dialog("Verifique a origem do arquivo a ser copiado, informado: "+ sSourcePath);
        return False;

      if( sDestinationPath == '' ):
        sublime.message_dialog("Verifique o destino do arquivo a ser copiado, informado: "+ sDestinationPath);
        return False;

      if( sComando == 'cp' ):
        sComandoShell = sComando +" -v " + sSourcePath + " " + sDestinationPath;
      else:
        sComandoShell =  " cd " + sDestinationPath + " && " + sComando + " " + sSourcePath;

      output = subprocess.check_output(sComandoShell, shell = True);
      return output.decode('utf8');

    except:
      self.defineStatus("Erro ao executar o comando "+ sComando +"! -> " + sComandoShell);
      # self.openTerminal("Erro ao executar o comando "+sComando+"! -> " + sComandoShell);

  '''
    Abre a janela do terminal com saida do console
  '''
  def openTerminal(self, sSaida):

    self.output_view = self.view.window().create_output_panel("textarea");
    window = sublime.active_window();
    window.run_command("show_panel", {"panel": "output.textarea"});
    self.output_view.set_read_only(False);
    self.output_view.run_command("append", {"characters": sSaida});