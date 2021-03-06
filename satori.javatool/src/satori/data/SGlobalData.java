package satori.data;

import static satori.data.SAttributeData.getBlobAttrMap;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

import satori.common.SPair;
import satori.session.SSession;
import satori.task.STaskHandler;
import satori.thrift.gen.Global;

class SGlobalData {
	static Map<String, SBlob> getJudges(STaskHandler handler) throws Exception {
		handler.log("Loading judges...");
		Global.Iface iface = new Global.Client(handler.getProtocol());
		long id = iface.Global_get_instance(SSession.getToken()).getId();
		return Collections.unmodifiableMap(getBlobAttrMap(iface.Global_judges_get_map(SSession.getToken(), id)));
	}
	
	static Map<String, String> getDispatchers(STaskHandler handler) throws Exception {
		handler.log("Loading dispatchers...");
		Global.Iface iface = new Global.Client(handler.getProtocol());
		return iface.Global_get_dispatchers(SSession.getToken());
	}
	static Map<String, String> getAccumulators(STaskHandler handler) throws Exception {
		handler.log("Loading accumulators...");
		Global.Iface iface = new Global.Client(handler.getProtocol());
		return iface.Global_get_accumulators(SSession.getToken());
	}
	static Map<String, String> getReporters(STaskHandler handler) throws Exception {
		handler.log("Loading reporters...");
		Global.Iface iface = new Global.Client(handler.getProtocol());
		return iface.Global_get_reporters(SSession.getToken());
	}
	
	static List<SPair<String, String>> convertToList(Map<String, String> map) {
		List<SPair<String, String>> result = new ArrayList<SPair<String, String>>();
		for (Map.Entry<String, String> entry : map.entrySet()) result.add(new SPair<String, String>(entry.getKey(), entry.getValue()));
		Collections.sort(result, new Comparator<SPair<String, String>>() {
			@Override public int compare(SPair<String, String> p1, SPair<String, String> p2) { return p1.first.compareTo(p2.first); }
		});
		return Collections.unmodifiableList(result);
	}
}
