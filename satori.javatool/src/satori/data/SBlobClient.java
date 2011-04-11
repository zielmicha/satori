package satori.data;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.StringWriter;
import java.io.Writer;
import java.net.HttpURLConnection;
import java.net.URL;

import org.apache.commons.io.IOUtils;

import satori.session.SSession;
import satori.task.STaskManager;

public class SBlobClient {
	private static String getUploadAddress() throws Exception {
		SSession session = SSession.get();
		if (session == null) throw new Exception("Not logged in");
		return "https://" + session.getHost() + ":" + session.getBlobsPort() + "/blob/upload";
	}
	private static String getDownloadAddress(String hash) throws Exception {
		SSession session = SSession.get();
		if (session == null) throw new Exception("Not logged in");
		return "https://" + session.getHost() + ":" + session.getBlobsPort() + "/blob/download/" + hash;
	}
	
	private static HttpURLConnection putBlobSetup(File file) throws Exception {
		URL url = new URL(getUploadAddress());
		HttpURLConnection connection = (HttpURLConnection)url.openConnection();
		connection.setDoOutput(true);
		connection.setUseCaches(false);
		connection.setRequestMethod("PUT");
		connection.setRequestProperty("Cookie", "satori_token=" + SSession.getToken());
		connection.setRequestProperty("Content-length", String.valueOf(file.length()));
		connection.setRequestProperty("Filename", file.getName());
		return connection;
	}
	private static HttpURLConnection getBlobSetup(String hash) throws Exception {
		URL url = new URL(getDownloadAddress(hash));
		HttpURLConnection connection = (HttpURLConnection)url.openConnection();
		connection.setUseCaches(false);
		connection.setRequestMethod("GET");
		connection.setRequestProperty("Cookie", "satori_token=" + SSession.getToken());
		connection.setRequestProperty("Content-length", "0");
		return connection;
	}
	private static void checkResponse(HttpURLConnection connection) throws Exception {
		int response = connection.getResponseCode();
		if (response != HttpURLConnection.HTTP_OK) throw new Exception("Error saving blob: " + response + " " + connection.getResponseMessage());
	}
	private static void putBlob(HttpURLConnection connection, File file) throws Exception {
		InputStream in = new FileInputStream(file);
		try {
			OutputStream out = connection.getOutputStream();
			try { IOUtils.copy(in, out); }
			finally { IOUtils.closeQuietly(out); }
		} finally { IOUtils.closeQuietly(in); }
	}
	private static String readResponse(HttpURLConnection connection) throws Exception {
		InputStream in = connection.getInputStream();
		Writer result = new StringWriter();
		try { IOUtils.copy(in, result); }
		finally { IOUtils.closeQuietly(in); }
		return result.toString();
	}
	private static void getBlob(HttpURLConnection connection, File file) throws Exception {
		InputStream in = connection.getInputStream();
		try {
			OutputStream out = new FileOutputStream(file);
			try { IOUtils.copy(in, out); }
			finally { IOUtils.closeQuietly(out); }
		} finally { IOUtils.closeQuietly(in); }
	}
	
	public static String putBlob(File file) throws Exception {
		STaskManager.log("Saving blob...");
		HttpURLConnection connection = putBlobSetup(file);
		putBlob(connection, file);
		checkResponse(connection);
		return readResponse(connection);
	}
	
	public static InputStream getBlobStream(String hash) throws Exception {
		HttpURLConnection connection = getBlobSetup(hash);
		checkResponse(connection);
		return connection.getInputStream();
	}
	public static void getBlob(String hash, File file) throws Exception {
		STaskManager.log("Loading blob...");
		HttpURLConnection connection = getBlobSetup(hash);
		checkResponse(connection);
		getBlob(connection, file);
	}
}
