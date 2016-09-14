import Tkinter
import ttk
import sys


class XNATQCGUI(ttk.Frame):
    """GUI for editing QC."""
    def __init__(self, root, project, subject, session, qobject, qtype):
        """Init method."""
        ttk.Frame.__init__(self,
                           root,
                           width=500,
                           height=400)
        self.root = root
        self.root.title(u"Edit QC status on XNAT")
        # build frame
        # self.mainframe = ttk.Frame(self.root)

        # text labels
        self.label = ttk.Label(root, text=u"Xnatqc",
                               font=("Helvetica", 32))

        # Xnat info:
        self.xnatdata = ttk.Labelframe(root, text='XNAT information')
        self.project = ttk.Label(self.xnatdata, text=u"Project: %s" % project)
        self.subject = ttk.Label(self.xnatdata, text=u"Subject: %s" % subject)
        self.session = ttk.Label(self.xnatdata, text=u"Session: %s" % session)
        self.qobject = ttk.Label(self.xnatdata, text=u"QC obj: %s" % qobject)
        self.qtype = ttk.Label(self.xnatdata, text=u"Type: %s" % qtype)

        # Frame label for QC status form
        self.lfdata = ttk.Labelframe(root, text='Quality Control Form')
        # QC Status
        self.qcstatus_var = Tkinter.StringVar()
        self.qcstatus_var.set('                ')
        self.qlabel = ttk.Label(self.lfdata, text=u"QC Status")
        self.qcstatus = ttk.OptionMenu(self.lfdata, self.qcstatus_var,
                                       '', 'Passed', 'Good', 'OK', 'Poor',
                                       'Do Not Run', 'Rerun', 'Needs QA',
                                       'Needs Edits', 'Bad', 'Failed')
        # Method
        self.method_var = Tkinter.StringVar()
        self.mlabel = ttk.Label(self.lfdata, text=u"Method:")
        self.method = ttk.Entry(self.lfdata, textvariable=self.method_var)
        self.method_var.set('')
        # Notes
        self.notes_var = Tkinter.StringVar()
        self.nlabel = ttk.Label(self.lfdata, text=u"Notes:")
        self.notes = ttk.Entry(self.lfdata, textvariable=self.notes_var)
        self.notes_var.set('')

        # buttons
        self.stop = ttk.Button(root, command=self.stop,
                               text='Close')
        self.submit = ttk.Button(root, command=self.submit,
                                 text='Submit')

        # Grid:
        self.grid(column=0, row=0, columnspan=4, rowspan=5)
        self.label.grid(columnspan=2, column=1, row=0)
        self.xnatdata.grid(columnspan=4, column=0, row=1)
        west_stk = Tkinter.N+Tkinter.S+Tkinter.W
        self.project.grid(column=0, row=0, sticky=west_stk)
        self.subject.grid(column=0, row=1, sticky=west_stk)
        self.session.grid(column=0, row=2, sticky=west_stk)
        self.qobject.grid(column=0, row=3, sticky=west_stk)
        self.qtype.grid(column=0, row=4, sticky=west_stk)
        self.lfdata.grid(columnspan=4, column=0, row=2)
        self.qlabel.grid(columnspan=1, column=0, row=0, sticky=west_stk)
        self.qcstatus.grid(columnspan=3, column=1, row=0, sticky=west_stk)
        self.mlabel.grid(columnspan=1, column=0, row=1, sticky=west_stk)
        self.method.grid(columnspan=3, column=1, row=1, sticky=west_stk)
        self.nlabel.grid(columnspan=1, column=0, row=2, sticky=west_stk)
        self.notes.grid(columnspan=3, rowspan=3, column=1, row=2,
                        sticky=west_stk)
        self.stop.grid(column=1, row=3)
        self.submit.grid(column=2, row=3)

    def stop(self):
        sys.exit()

    def submit(self):
        print "SUBMIT"


root = Tkinter.Tk()
root.geometry('500x400')
root.configure(background='grey')
makeGUI = XNATQCGUI(root, 'ADNI', 'test', 'test_2012', '101', 'T1')
root.mainloop()
