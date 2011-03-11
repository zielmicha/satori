package satori.problem.ui;

import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.List;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

import satori.common.SException;
import satori.common.SListener0;
import satori.common.SListener1;
import satori.common.SView;
import satori.common.ui.STabPane;
import satori.common.ui.STabbedPane;
import satori.common.ui.STabs;
import satori.main.SFrame;
import satori.problem.STestSuiteSnap;
import satori.problem.impl.SProblemImpl;
import satori.problem.impl.STestSuiteImpl;
import satori.test.STestSnap;
import satori.test.impl.STestFactory;
import satori.test.impl.STestImpl;

public class SProblemPane implements STabPane, SView {
	private final SProblemImpl problem;
	private final STabs parent;
	
	private STabbedPane tabs;
	private SProblemInfoPane info_pane;
	private STestListPane test_list_pane;
	private STestSuiteListPane suite_list_pane;
	private SView tab_view;
	
	private final STestFactory test_factory = new STestFactory() {
		@Override public STestImpl create(STestSnap snap) throws SException {
			return STestImpl.create(snap, problem);
		}
		@Override public STestImpl createNew() {
			return STestImpl.createNew(problem);
		}
	};
	
	private JScrollPane scroll_pane;
	private JPanel main_pane;
	private JLabel status_label;
	private JPanel button_pane;
	private JButton save_button, reload_button, delete_button, close_button;
	
	private SProblemPane(SProblemImpl problem, STabs parent) {
		this.problem = problem;
		this.parent = parent;
		initialize();
	}
	
	@Override public JComponent getPane() { return scroll_pane; }
	
	private static class TabModel implements STabs.TabModel {
		private final SProblemImpl problem;
		public TabModel(SProblemImpl problem) { this.problem = problem; }
		@Override public String getTitle() {
			return problem.getName().isEmpty() ? "(Problem)" : problem.getName();
		}
	}
	public static SProblemPane open(SProblemImpl problem, STabs parent) {
		SProblemPane self = new SProblemPane(problem, parent);
		problem.setTestListListener(self.test_list_pane);
		problem.setTestSuiteListListener(self.suite_list_pane);
		problem.addView(self);
		self.tab_view = parent.openPane(new TabModel(problem), self);
		problem.addView(self.tab_view);
		self.tabs.addParentView(self.tab_view);
		return self;
	}
	@Override public boolean hasUnsavedData() {
		return problem.isModified() || tabs.hasUnsavedData();
	}
	@Override public void close() {
		problem.close();
	}
	
	private final SListener0 new_test_listener = new SListener0() {
		@Override public void call() {
			STestSuiteImpl suite = STestSuiteImpl.createNewTest(problem);
			STestSuitePane suite_pane = new STestSuitePane(suite, tabs, test_factory);
			suite_pane.getTestPane().add(suite.getTests());
			suite_pane.open();
		}
	};
	private final SListener1<List<STestSnap>> open_tests_listener = new SListener1<List<STestSnap>>() {
		@Override public void call(List<STestSnap> snaps) {
			STestSuiteImpl suite;
			try { suite = STestSuiteImpl.createNew(snaps, problem); }
			catch(SException ex) { SFrame.showErrorDialog(ex); return; }
			STestSuitePane suite_pane = new STestSuitePane(suite, tabs, test_factory);
			suite_pane.getTestPane().add(suite.getTests());
			suite_pane.open();
		}
	};
	private final SListener0 new_suite_listener = new SListener0() {
		@Override public void call() {
			STestSuiteImpl suite = STestSuiteImpl.createNew(problem);
			STestSuitePane suite_pane = new STestSuitePane(suite, tabs, test_factory);
			suite_pane.open();
		}
	};
	private final SListener1<STestSuiteSnap> open_suite_listener = new SListener1<STestSuiteSnap>() {
		@Override public void call(STestSuiteSnap snap) {
			STestSuiteImpl suite;
			try { suite = STestSuiteImpl.create(snap, problem); }
			catch(SException ex) { SFrame.showErrorDialog(ex); return; }
			STestSuitePane suite_pane = new STestSuitePane(suite, tabs, test_factory);
			suite_pane.getTestPane().add(suite.getTests());
			suite_pane.open();
		}
	};
	
	private void saveRequest() {
		try { if (problem.isRemote()) problem.save(); else problem.create(); }
		catch(SException ex) { SFrame.showErrorDialog(ex); return; }
	}
	private void reloadRequest() {
		if (!problem.isRemote()) return;
		try { problem.reload(); }
		catch(SException ex) { SFrame.showErrorDialog(ex); return; }
	}
	private void deleteRequest() {
		if (!problem.isRemote() || !SFrame.showWarningDialog("The problem will be deleted.")) return;
		try { problem.delete(); }
		catch(SException ex) { SFrame.showErrorDialog(ex); return; }
	}
	private void closeRequest() {
		if (hasUnsavedData() && !SFrame.showWarningDialog("This tab contains unsaved data.")) return;
		close();
		parent.closePane(this);
	}
	
	private void initialize() {
		tabs = new STabbedPane();
		info_pane = new SProblemInfoPane(problem);
		test_list_pane = new STestListPane(new_test_listener, open_tests_listener);
		suite_list_pane = new STestSuiteListPane(new_suite_listener, open_suite_listener);
		
		main_pane = new JPanel(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();
		c.gridx = 0; c.gridy = 0; c.fill = GridBagConstraints.HORIZONTAL; c.weightx = 1.0; c.weighty = 0.0; c.gridwidth = 2;
		status_label = new JLabel();
		main_pane.add(status_label, c);
		c.gridx = 0; c.gridy = 1; c.fill = GridBagConstraints.HORIZONTAL; c.weightx = 1.0; c.weighty = 0.0; c.gridwidth = 2;
		button_pane = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
		save_button = new JButton("Save");
		save_button.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { saveRequest(); }
		});
		button_pane.add(save_button);
		reload_button = new JButton("Reload");
		reload_button.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { reloadRequest(); }
		});
		button_pane.add(reload_button);
		delete_button = new JButton("Delete");
		delete_button.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { deleteRequest(); }
		});
		button_pane.add(delete_button);
		close_button = new JButton("Close");
		close_button.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { closeRequest(); }
		});
		button_pane.add(close_button);
		main_pane.add(button_pane, c);
		info_pane.getPane().setBorder(BorderFactory.createTitledBorder("Problem properties"));
		c.gridx = 0; c.gridy = 2; c.fill = GridBagConstraints.BOTH; c.weightx = 1.0; c.weighty = 0.0; c.gridwidth = 2;
		main_pane.add(info_pane.getPane(), c);
		test_list_pane.getPane().setBorder(BorderFactory.createTitledBorder("Tests"));
		test_list_pane.getPane().setPreferredSize(new Dimension(320, 110));
		c.gridx = 0; c.gridy = 3; c.fill = GridBagConstraints.BOTH; c.weightx = 0.5; c.weighty = 0.4; c.gridwidth = 1;
		main_pane.add(test_list_pane.getPane(), c);
		suite_list_pane.getPane().setBorder(BorderFactory.createTitledBorder("Test suites"));
		suite_list_pane.getPane().setPreferredSize(new Dimension(320, 110));
		c.gridx = 1; c.gridy = 3; c.fill = GridBagConstraints.BOTH; c.weightx = 0.5; c.weighty = 0.4; c.gridwidth = 1;
		main_pane.add(suite_list_pane.getPane(), c);
		tabs.getPane().setPreferredSize(new Dimension(640, 370));
		c.gridx = 0; c.gridy = 4; c.fill = GridBagConstraints.BOTH; c.weightx = 1.0; c.weighty = 0.6; c.gridwidth = 2;
		main_pane.add(tabs.getPane(), c);
		scroll_pane = new JScrollPane(main_pane);
		update();
	}
	
	@Override public void update() {
		reload_button.setEnabled(problem.isRemote());
		delete_button.setEnabled(problem.isRemote());
		String status_text = "";
		if (problem.isRemote()) {
			if (problem.isOutdated()) status_text = "outdated";
		} else {
			if (problem.isOutdated()) status_text = "deleted";
			else status_text = "new";
		}
		if (problem.isModified()) {
			if (!status_text.isEmpty()) status_text += ", ";
			status_text += "modified";
		}
		if (status_text.isEmpty()) status_text = "saved";
		status_label.setText("Status: " + status_text);
		info_pane.update();
	}
}
