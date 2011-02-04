package satori.test.ui;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JComponent;
import javax.swing.JLabel;

import satori.test.impl.STestResult;

public class SResultStatusRowView implements SSolutionRowView {
	private JComponent pane;
	
	public SResultStatusRowView() {
		initialize();
	}
	
	@Override public JComponent getPane() { return pane; }
	
	private void initialize() {
		pane = new Box(BoxLayout.X_AXIS);
		JLabel label = new JLabel("Status");
		SDimension.setLabelSize(label);
		pane.add(label);
		pane.add(Box.createHorizontalGlue());
	}
	
	@Override public void addColumn(STestResult result, int index) {
		int pane_index = (index+1 < pane.getComponentCount()) ? index+1 : -1;
		pane.add(new SResultStatusItemView(result).getPane(), pane_index);
	}
	@Override public void removeColumn(int index) {
		pane.remove(index+1);
	}
}
