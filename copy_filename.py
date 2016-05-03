import sublime, sublime_plugin, os, string

class CopyFilenameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if len(self.view.file_name()) > 0:
            filename = os.path.split(self.view.file_name())[1]
            sublime.set_clipboard(filename)
            sublime.status_message("Nome do arquivo copiado para o seu louvavel Ctrl + V -> %s" % filename)

    def is_enabled(self):
        return self.view.file_name() and len(self.view.file_name()) > 0
