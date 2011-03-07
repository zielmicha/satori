package satori.problem;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import satori.common.SAssert;
import satori.common.SException;
import satori.common.SListener1;
import satori.common.SPair;
import satori.common.SReference;
import satori.common.SView;
import satori.test.STestBasicReader;
import satori.test.STestSnap;
import satori.thrift.STestSuiteData;

public class STestSuiteSnap implements STestSuiteReader {
	private final STestList test_list;
	
	private long id;
	private long problem_id;
	private String name;
	private String desc;
	private List<STestSnap> tests;
	private List<SPair<String, String>> dispatchers;
	private List<SPair<String, String>> accumulators;
	private List<SPair<String, String>> reporters;
	
	private final List<SView> views = new ArrayList<SView>();
	private final List<SReference> refs = new ArrayList<SReference>();
	private final SListener1<STestSnap> test_deleted_listener = new SListener1<STestSnap>() {
		@Override public void call(STestSnap test) { testDeleted(test); }
	};
	
	@Override public boolean hasId() { return true; }
	@Override public long getId() { return id; }
	@Override public long getProblemId() { return problem_id; }
	@Override public String getName() { return name; }
	@Override public String getDescription() { return desc; }
	@Override public List<STestSnap> getTests() { return Collections.unmodifiableList(tests); }
	@Override public List<SPair<String, String>> getDispatchers() { return dispatchers; }
	@Override public List<SPair<String, String>> getAccumulators() { return accumulators; }
	@Override public List<SPair<String, String>> getReporters() { return reporters; }
	
	public boolean isComplete() { return tests != null; }
	
	private STestSuiteSnap(STestList test_list) {
		this.test_list = test_list;
	}
	
	private void createTestList(List<? extends STestBasicReader> source) {
		tests = new ArrayList<STestSnap>();
		for (STestBasicReader test : source) tests.add(test_list.getTest(test));
	}
	private void addTestDeletedListeners() {
		for (STestSnap test : tests) test.addDeletedListener(test_deleted_listener);
	}
	private void removeTestDeletedListeners() {
		for (STestSnap test : tests) test.removeDeletedListener(test_deleted_listener);
	}
	
	public static STestSuiteSnap create(STestList test_list, STestSuiteReader source) {
		SAssert.assertEquals(source.getProblemId(), test_list.getProblemId(), "Problem ids don't match");
		STestSuiteSnap self = new STestSuiteSnap(test_list);
		self.id = source.getId();
		self.problem_id = source.getProblemId();
		self.name = source.getName();
		self.desc = source.getDescription();
		self.createTestList(source.getTests());
		self.addTestDeletedListeners();
		self.dispatchers = source.getDispatchers();
		self.accumulators = source.getAccumulators();
		self.reporters = source.getReporters();
		return self;
	}
	public static STestSuiteSnap createBasic(STestList test_list, STestSuiteBasicReader source) {
		SAssert.assertEquals(source.getProblemId(), test_list.getProblemId(), "Problem ids don't match");
		STestSuiteSnap self = new STestSuiteSnap(test_list);
		self.id = source.getId();
		self.problem_id = source.getProblemId();
		self.name = source.getName();
		self.desc = source.getDescription();
		self.tests = null;
		self.dispatchers = null;
		self.accumulators = null;
		self.reporters = null;
		return self;
	}
	
	public void set(STestSuiteReader source) {
		SAssert.assertEquals(source.getId(), getId(), "Test suite ids don't match");
		SAssert.assertEquals(source.getProblemId(), getProblemId(), "Problem ids don't match");
		name = source.getName();
		desc = source.getDescription();
		if (tests != null) removeTestDeletedListeners();
		createTestList(source.getTests());
		addTestDeletedListeners();
		dispatchers = source.getDispatchers();
		accumulators = source.getAccumulators();
		reporters = source.getReporters();
		notifyModified();
	}
	public void setBasic(STestSuiteBasicReader source) {
		SAssert.assertEquals(source.getId(), getId(), "Test suite ids don't match");
		SAssert.assertEquals(source.getProblemId(), getProblemId(), "Problem ids don't match");
		name = source.getName();
		desc = source.getDescription();
		notifyModified();
	}
	public void reload() throws SException { set(STestSuiteData.load(id)); }
	
	private void testDeleted(STestSnap test) {
		tests.remove(test);
		//for (SView view : views) view.update(); //TODO: is this necessary?
		for (SReference ref : refs) ref.notifyModified();
	}
	
	private void notifyModified() {
		for (SView view : views) view.update();
		for (SReference ref : refs) ref.notifyModified();
	}
	public void notifyDeleted() {
		for (SReference ref : refs) ref.notifyDeleted();
	}
	
	public void addView(SView view) { views.add(view); }
	public void removeView(SView view) { views.remove(view); }
	
	public void addReference(SReference ref) { refs.add(ref); }
	public void removeReference(SReference ref) { refs.remove(ref); }
}
