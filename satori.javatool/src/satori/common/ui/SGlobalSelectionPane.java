package satori.common.ui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Vector;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.SwingConstants;

import satori.common.SListener0;
import satori.common.SPair;
import satori.main.SFrame;
import satori.metadata.SParametersMetadata;
import satori.task.STaskException;
import satori.task.STaskHandler;
import satori.task.STaskManager;

public class SGlobalSelectionPane implements SPane {
	public static interface Loader {
		List<SPair<String, String>> getList(STaskHandler handler) throws STaskException;
		SParametersMetadata parse(STaskHandler handler, String name, String content) throws STaskException;
	};
	
	private final Loader loader;
	private final boolean multiple, empty;
	private final SListener0 listener;
	private List<SParametersMetadata> selection;
	private JComponent pane;
	private JButton clear_button;
	private JButton label;
	private Font set_font, unset_font;
	private Color default_color;
	
	public SGlobalSelectionPane(Loader loader, boolean multiple, boolean empty, SListener0 listener) {
		this.loader = loader;
		this.multiple = multiple;
		this.empty = empty;
		this.listener = listener;
		initialize();
	}
	
	@Override public JComponent getPane() { return pane; }
	
	public List<SParametersMetadata> getSelection() { return selection; }
	public SParametersMetadata getFirstSelected() { return selection.isEmpty() ? null : selection.get(0); }
	
	public void setSelection(List<SParametersMetadata> params) {
		selection = params;
		StringBuilder text = null;
		for (SParametersMetadata p : params) {
			if (text != null) text.append(",");
			else text = new StringBuilder();
			text.append(p.getName());
		}
		pane.setBackground(text != null || empty ? default_color : Color.YELLOW);
		label.setFont(text != null ? set_font : unset_font);
		label.setText(text != null ? text.toString() : "Not set");
	}
	public void setSelection(SParametersMetadata params) {
		if (params != null) selection = Collections.singletonList(params);
		else selection = Collections.emptyList();
		pane.setBackground(params != null || empty ? default_color : Color.YELLOW);
		label.setFont(params != null ? set_font : unset_font);
		label.setText(params != null ? params.getName() : "Not set");
	}
	public void clearSelection() {
		selection = Collections.emptyList();
		pane.setBackground(empty ? default_color : Color.YELLOW);
		label.setFont(unset_font);
		label.setText("Not set");
	}
	
	private static class LoadDialog {
		private final Loader loader;
		private final boolean multiple;
		private JDialog dialog;
		private JList list;
		private boolean confirmed = false;
		
		public LoadDialog(Loader loader, boolean multiple) {
			this.loader = loader;
			this.multiple = multiple;
			initialize();
		}
		
		private void initialize() {
			dialog = new JDialog(SFrame.get().getFrame(), "Select", true);
			dialog.getContentPane().setLayout(new BorderLayout());
			list = new JList();
			list.setSelectionMode(multiple ? ListSelectionModel.MULTIPLE_INTERVAL_SELECTION : ListSelectionModel.SINGLE_SELECTION);
			list.addMouseListener(new MouseAdapter() {
				@Override public void mouseClicked(MouseEvent e) {
					if (e.getClickCount() != 2) return;
					e.consume();
					confirmed = true;
					dialog.setVisible(false);
				}
			});
			JScrollPane list_pane = new JScrollPane(list);
			list_pane.setPreferredSize(new Dimension(200, 100));
			dialog.getContentPane().add(list_pane, BorderLayout.CENTER);			
			JPanel button_pane = new JPanel(new FlowLayout(FlowLayout.CENTER));
			JButton confirm = new JButton("OK");
			confirm.addActionListener(new ActionListener() {
				@Override public void actionPerformed(ActionEvent e) {
					confirmed = true;
					dialog.setVisible(false);
				}
			});
			button_pane.add(confirm);
			JButton cancel = new JButton("Cancel");
			cancel.addActionListener(new ActionListener() {
				@Override public void actionPerformed(ActionEvent e) {
					dialog.setVisible(false);
				}
			});
			button_pane.add(cancel);
			dialog.getContentPane().add(button_pane, BorderLayout.SOUTH);
			dialog.pack();
			dialog.setLocationRelativeTo(SFrame.get().getFrame());
		}
		
		public List<SPair<String, String>> process() throws STaskException {
			List<SPair<String, String>> source;
			STaskHandler handler = STaskManager.getHandler();
			try { source = loader.getList(handler); }
			finally { handler.close(); }
			Vector<String> names = new Vector<String>();
			for (SPair<String, String> p : source) names.add(p.first);
			list.setListData(names);
			dialog.setVisible(true);
			if (!confirmed) return null;
			int[] indices = list.getSelectedIndices();
			List<SPair<String, String>> result = new ArrayList<SPair<String, String>>();
			for (int i : indices) result.add(source.get(i));
			return result;
		}
	}
	
	private void load() {
		LoadDialog dialog = new LoadDialog(loader, multiple);
		STaskHandler handler = STaskManager.getHandler();
		try {
			List<SPair<String, String>> result = dialog.process();
			if (result == null) return;
			List<SParametersMetadata> params = new ArrayList<SParametersMetadata>();
			for (SPair<String, String> p : result) params.add(loader.parse(handler, p.first, p.second));
			setSelection(Collections.unmodifiableList(params));
			listener.call();
		}
		catch(STaskException ex) {}
		finally { handler.close(); }
	}
	private void clear() {
		clearSelection();
		listener.call();
	}
	
	private void initialize() {
		pane = new JPanel(new SLayoutManagerAdapter() {
			@Override public void layoutContainer(Container parent) {
				Dimension dim = parent.getSize();
				clear_button.setBounds(0, (dim.height-13)/2, 13, 13);
				label.setBounds(15, 0, dim.width-15, dim.height);
			}
		});
		byte[] icon = {71,73,70,56,57,97,7,0,7,0,-128,1,0,-1,0,0,-1,-1,-1,33,-7,4,1,10,0,1,0,44,0,0,0,0,7,0,7,0,0,2,13,12,126,6,-63,-72,-36,30,76,80,-51,-27,86,1,0,59};
		clear_button = new JButton(new ImageIcon(icon));
		clear_button.setMargin(new Insets(0, 0, 0, 0));
		clear_button.setToolTipText("Clear");
		clear_button.setFocusable(false);
		clear_button.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { clear(); }
		});
		pane.add(clear_button);
		label = new JButton();
		label.setBorder(BorderFactory.createEmptyBorder(0, 1, 0, 1));
		label.setBorderPainted(false);
		label.setContentAreaFilled(false);
		label.setOpaque(false);
		label.setHorizontalAlignment(SwingConstants.LEADING);
		label.addActionListener(new ActionListener() {
			@Override public void actionPerformed(ActionEvent e) { load(); }
		});
		pane.add(label);
		set_font = label.getFont().deriveFont(Font.PLAIN);
		unset_font = label.getFont().deriveFont(Font.ITALIC);
		default_color = pane.getBackground();
	}
}
