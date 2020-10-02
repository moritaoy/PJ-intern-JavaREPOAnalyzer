package com.pjintern.demo.logic;

import java.io.IOException;

import org.springframework.stereotype.Service;
import org.springframework.ui.Model;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import okhttp3.Call;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

@Service
public class RequestLogic {
	public Model user_get(Model model, String s) {
		model.addAttribute("request_userId", s);
		
		String[] user_list = s.split(" ", 0);
		OkHttpClient okHttpClient = new OkHttpClient();
		MediaType MIMEType = MediaType.parse("application/json; charset=utf-8");
		String api_url = "https://5ol5n0rkhb.execute-api.ap-northeast-1.amazonaws.com/dev/user?userId=";
		
		ObjectMapper res_mapper = new ObjectMapper();
		ObjectNode res_node = res_mapper.createObjectNode();
		for (int i = 0; i < user_list.length; i++) {
			String target = user_list[i];
			if(target=="")continue;
			Request request = new Request.Builder().url(api_url + target).get().build();
			Call call = okHttpClient.newCall(request);
			try (Response response = call.execute()) {
				if (response.body() == null) {
					res_node.put(target, "\"{\"message\": \"Internal Server Error\"}\"");
					continue;
				}
				String responce_str = response.body().string();
				res_node.put(target, responce_str);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		try {
			String json = res_mapper.writeValueAsString(res_node);
			model.addAttribute("data_json", json);
			return model;
		} catch(Exception e) {
			e.printStackTrace();
		}
		return model;
	}

	public Model analyze_post(Model model, String s) {

		model.addAttribute("request_address", s);
		if (!s.startsWith("https://github.com/")) {
			model.addAttribute("msg_warning", "アドレスは https://github.com/ で始まらなければなりません");
			return model;
		}
		if (s.length() <= 20) {
			model.addAttribute("msg_warning", "アドレスの情報が足りません。少なくともGithub IDと リポジトリ名までが含まれた有効なアドレスを入力してください。");
			return model;
		}
		String git_api = "https://api.github.com/repos/";
		String api_add = s.substring(19);
		String userId, repoName;
		String[] address_parsed = api_add.split("/", 0);
		if (address_parsed.length < 2) {
			model.addAttribute("msg_warning", "アドレスの情報が足りません。少なくともGithub IDと リポジトリ名までが含まれた有効なアドレスを入力してください。");
			return model;
		}
		userId = address_parsed[0];
		repoName = address_parsed[1];

		api_add = userId + "/" + repoName;

		OkHttpClient okHttpClient = new OkHttpClient();
		MediaType MIMEType = MediaType.parse("application/json; charset=utf-8");

		Request request_git = new Request.Builder().url(git_api + api_add).get().build();

		Call call_git = okHttpClient.newCall(request_git);
		try (Response response = call_git.execute()) {
			if (!response.isSuccessful()) {
				model.addAttribute("msg_warning", "該当するリポジトリにアクセスできませんでした。リポジトリがプライベートであるか、URLが不正です。");
				return model;
			}
			if (response.body() == null) {
				model.addAttribute("msg_warning", "該当するリポジトリにアクセスできませんでした。リポジトリがプライベートであるか、URLが不正です。");
				return model;
			}
			String responce_str = response.body().string();
			ObjectMapper mapper = new ObjectMapper();
			JsonNode node = mapper.readTree(responce_str);

			JsonNode value = node.findValue("private");
			if (value == null) {
				model.addAttribute("msg_warning", "該当するリポジトリにアクセスできませんでした。リポジトリがプライベートであるか、URLが不正です。");
				return model;
			}
			if (node.get("private").booleanValue()) {
				model.addAttribute("msg_warning", "該当するリポジトリにアクセスできませんでした。リポジトリがプライベートであるか、URLが不正です。");
				return model;
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		RequestBody body = RequestBody.create(MIMEType,
				"{\"userId\": \"" + userId + "\", \"repoName\": \"" + repoName + "\"}");
		Request request_aws = new Request.Builder()
				.url("https://5ol5n0rkhb.execute-api.ap-northeast-1.amazonaws.com/dev/analyze").post(body).build();

		Call call = okHttpClient.newCall(request_aws);
		try {
			Response response = call.execute();
			if (response.body() == null) {
				model.addAttribute("msg_warning", "解析サーバーへのリクエストに失敗しました。しばらく経ってから再度お試しください。再発する場合は、管理者へご連絡ください。");
				return model;
			}
			String responce_str = response.body().string();
			ObjectMapper mapper = new ObjectMapper();
			JsonNode node = mapper.readTree(responce_str);

			JsonNode value = node.findValue("message");

			if (value == null) {
				model.addAttribute("msg_warning", "解析サーバーへのリクエストに失敗しました。しばらく経ってから再度お試しください。再発する場合は、管理者へご連絡ください。");
				return model;
			}
			if (!response.isSuccessful()) {
				model.addAttribute("msg_warning", node.get("message").textValue());
				return model;
			} else {
				model.addAttribute("msg_success", node.get("message").textValue());
				model.addAttribute("request_userId", userId);
				model.addAttribute("request_address", "");
				return model;
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		model.addAttribute("msg_warning", "Internal Server Error. しばらく経ってから再度お試しください。");
		return model;
	}

}