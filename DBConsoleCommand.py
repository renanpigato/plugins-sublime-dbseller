# -*- coding: cp1252 -*-
import sublime, sublime_plugin, subprocess, urllib.request, os, string, json, ast, sys, re

class DbConsoleCommand(sublime_plugin.TextCommand):

  def run(self, edit, **kwargs):

    opcoesMenu = [];
    opcoesMenu.append("cvsGit::Status");
    opcoesMenu.append("cvsGit::Log");
    opcoesMenu.append("cvsGit::Diff");
    opcoesMenu.append("cvsGit::Diff com Revisão");
    opcoesMenu.append("cvsGit::Pull");
    opcoesMenu.append("cvsGit::Push");
    opcoesMenu.append("cvsGit::Whatchanged");
    opcoesMenu.append("Cvs::Tag");
    opcoesMenu.append("DBimpactos");
    opcoesMenu.append("DBreleases");
    opcoesMenu.append("Buscar Menu");

    '''
      Recebe como argumento o comando para chamar via hotkey
    '''
    if( kwargs != {} ):
      self.switchCase(None, kwargs['comando']);
      return True;

    window = sublime.active_window();
    window.show_quick_panel( opcoesMenu, self.menu, sublime.MONOSPACE_FONT );

  '''
    Switch do menu
  '''
  def switchCase(self, iOpcao, sComando = 'null'):

    #Cria um "dicionário" que relaciona função com a opção desejada
    aFuncoes = {
                 0  : [self.status     , 'status'],
                 1  : [self.log        , 'log'],
                 2  : [self.diff       , 'diff'],
                 3  : [self.diffRevisao, 'diffRevisao'],
                 4  : [self.pull       , 'pull'],
                 5  : [self.push       , 'push'],
                 6  : [self.whatchanged, 'whatchanged'],
                 7  : [self.tag        , 'tag'],
                 8  : [self.impactos   , 'impactos'],
                 9  : [self.releases   , 'releases'],
                 10 : [self.buscarMenu , 'buscarMenu']
               };

    #Verificar se o comando existe no dicionário
    if(sComando != 'null'):
      for item in aFuncoes:
        if sComando in aFuncoes.get(item, None):
          iOpcao = item;
          break;

    aFuncoes[iOpcao][0]();

  def menu(self, iOpcaoEscolhida):

    if( iOpcaoEscolhida >= 0 ):
      self.switchCase(iOpcaoEscolhida);

  '''
    Define Mensagem de status da janela
  '''
  def defineStatus (self, sMensagem):
    sublime.status_message( sMensagem );

  '''
    Solicita hash para commit
    Exemplo: -T00666 -e -m 'mensagem do commit'
  '''
  def push( self ):

    window = sublime.active_window();
    window.show_input_panel("Hash do commit ( Ex.: -T666 -e -m 'mensagem do commit' ):", '', self.confirmarPush, None, None);

  '''
    Abre mensagem de confirmação para o usuário e commita
  '''
  def confirmarPush(self, sHashCommit):

    if( sHashCommit.strip() == '' ):
      self.defineStatus("Hash do commit é obrigatório.");
      return False;

    sCaminhoArquivo = self.getArquivo();

    if sublime.ok_cancel_dialog("Deseja commitar o arquivo (Esc = não) ?\n" + "Arquivo -> " + sCaminhoArquivo + "\n Hash-> " + sHashCommit, "Claro que sim"):
      self.executaCvs( "add " + sHashCommit + ' ' + sCaminhoArquivo );
      self.commit();

      self.defineStatus ("Arquivo Comitado");
    else:
      self.defineStatus ("Arquivo NÃO Comitado");

  '''
    Retorna o caminho completo até o arquivo ativo
  '''
  def getArquivo(self):

    sCaminhoArquivo  = str( self.view.file_name() );

    aArquivo = sCaminhoArquivo.split('/');
    sCaminho = [];
    iPosicaoProjeto = 0;

    for iContador in range(len(aArquivo)):

      if( aArquivo[iContador] == 'dbportal_prj' ):
        iPosicaoProjeto = iContador;
      elif( aArquivo[iContador] == 'funcoes8' ):
        iPosicaoProjeto = iContador;

    for i in range(iPosicaoProjeto+1, len(aArquivo)):
      sCaminho.append(aArquivo[i]);

    sCaminhoArquivo = '/'.join([str(i) for i in sCaminho]);

    if ( sCaminhoArquivo.find('var/www') >= 0 ):
      sSearchedRootOfProject = re.search('[\/]*var\/www/.*?\/', sCaminhoArquivo);
      sCaminhoArquivo        = sCaminhoArquivo.replace(sSearchedRootOfProject.group(0), '');

    return sCaminhoArquivo;

  '''
    Commita arquivo no cvs
  '''
  def commit(self):

    output = self.executaCvs("push --no-interaction ");
    if(output):
      self.abreTerminal(output);

  '''
    cvsGit::Status
  '''
  def status(self):

    output = self.executaCvs("status");
    if(output):
      self.abreTerminal(output);

  '''
    cvsGit::Log
  '''
  def log(self):

    sPath  = str( self.view.file_name() );
    output = self.executaCvs( "log " + sPath );
    if(output):
      self.abreTerminal(output);

  '''
    cvsGit::Pull
  '''
  def pull(self):

    output = self.executaCvs("pull");
    if(output):
      self.abreTerminal(output);

  '''
    Executa os comandos no cvs
  '''
  def executaCvs(self, sComando, git = 'cvsgit'):

    iPosicao = 0;
    sProjeto = "dbportal_prj";

    sPath    = str( self.view.file_name() );
    iPosicao = sPath.find( "funcoes8", 0, len( sPath ) );

    if( iPosicao > 0 ):
      sProjeto = "funcoes8";

    try:

      if( sPath.find( sProjeto, 0, len( sPath ) ) >= 0 ):
        sComandoShell = "cd /var/www/" + sProjeto + " && " + git + " " + sComando;
      else:
        sSearchedProject = re.search('.*?\/', sPath.split('/var/www/')[1]);
        sSearchedProject = sSearchedProject.group(0).replace("/", "");
        sComandoShell    = "cd /var/www/" + sSearchedProject + " && " + git + " init " + " && " + git + " " + sComando;

      output = subprocess.check_output(sComandoShell, shell = True);
      output = output.decode('utf8');

      if( sPath.find( sProjeto, 0, len( sPath ) ) >= 0 ):
        return output;
      else:

        output = output.split("\n");
        del output[0];
        sPrint = "\n".join( str( e.strip()) for e in output );
        return sPrint;

    except:
      self.defineStatus("Erro ao executar o comando no cvsgit! -> " + sComandoShell);
      sublime.set_clipboard(sComandoShell);

  '''
    Solicita Tag para o arquivo ativo
  '''
  def tag(self):

    window = sublime.active_window();
    window.show_input_panel("Tag:", '', self.executaTag, None, None);

  '''
    Abre mensagem de confirmação para o usuário e taggea
  '''
  def executaTag(self, sTag):

    if( sTag.strip() == '' ):
      self.defineStatus('Tag é obrigatória.');
      return False;

    sCaminhoArquivo = self.getArquivo();

    if sublime.ok_cancel_dialog("Deseja taggear o arquivo (Esc = não) ? \n Arquivo -> " + sCaminhoArquivo + "\n Tag-> " + sTag, "Claro que sim"):
      self.executaCvs( "tag -F " + sTag + ' ' + sCaminhoArquivo, "cvs" );
      self.defineStatus ("Arquivo Taggeado");
    else:
      self.defineStatus ("Arquivo NÃO Taggeado");

  '''
    DBimpactos
  '''
  def impactos(self):

    sPath  = str( self.view.file_name() );
    output = subprocess.check_output("dbimpactos buscar " + sPath, shell = True)
    output = output.decode('utf8');
    self.abreTerminal(output);

  '''
    DBreleases
  '''
  def releases(self):

    output = subprocess.check_output("dbreleases");
    output = output.decode('utf8');
    output = output.split("\n");
    del output[0:3];

    sReleases = "Tag de Releases: \n";
    sReleases += "\n".join( str( "-> " + e.strip()) for e in output );
    self.abreTerminal(sReleases);

  '''
    Abre a janela do terminal com saida do console
  '''
  def abreTerminal(self, sSaida):

    self.output_view = self.view.window().create_output_panel("textarea");
    window = sublime.active_window();
    window.run_command("show_panel", {"panel": "output.textarea"});
    self.output_view.set_read_only(False);
    self.output_view.run_command("append", {"characters": sSaida});

  '''
    cvsGit::Whatchanged
  '''
  def whatchanged(self):

    window = sublime.active_window();
    window.show_input_panel("Tag de pesquisa para whatchanged:", '', self.executaWhatchanged, None, None);

  def executaWhatchanged(self, sTag = 'null'):

    if ( len( str( sTag ) ) == 0 ):
      output = self.executaCvs( "whatchanged" );
    else:
      output = self.executaCvs( "whatchanged -t " + sTag );

    if(output):
      self.abreTerminal(output);

  '''
    Executa diff recebendo como parametro a revisao
    Exemplo: 1.200
    Exemplo: 1.200 1.201
  '''
  def diffRevisao(self):

    window = sublime.active_window();
    window.show_input_panel("Revisão do diff (Ex.: 1.9 ou 1.9 1.10):", '', self.executaDiffRevisao, None, None);

  '''
    Wrapper do diff
  '''
  def executaDiffRevisao(self, sRevisao):
    self.diff( sRevisao );

  '''
    cvsGit::Diff
  '''
  def diff(self, sRevisao = 'null'):

    sCaminhoArquivo = self.getArquivo();

    if ( sRevisao != 'null' ):
      self.executaCvs( "diff " + sCaminhoArquivo + ' ' + sRevisao );
      return 1;

    self.executaCvs( "diff " + sCaminhoArquivo );

  '''
    Busca de menus
  '''
  def buscarMenu(self):

    try:

      sArquivo = str( self.getArquivo() );
      sRetorno = urllib.request.urlopen( 'http://utils.dbseller.com.br/buscaMenu.php?sBusca=' + sArquivo ).read();

      self.defineStatus( sRetorno.decode('iso-8859-1') );

    except Exception as error:
      self.defineStatus(" Erro ao buscar item de menu -> " + str(error));