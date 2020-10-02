package com.pjintern.demo.controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.pjintern.demo.logic.*;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class MainController {
	@Autowired
	private RequestLogic requestLogic;
	
	@RequestMapping(value =  {"", "/", "/index"})
	public String index(Model model) {
		model.addAttribute("msg", "Hello! Thymleaf!!");
		return "index";
	}
	
	@GetMapping(value =  {"/analyze"})
	public String analyze_get(Model model) {
		return "analyze";
	}
	
	@PostMapping(value =  {"/analyze"})
	public String analyze_post(Model model, @RequestParam("address")String ad) {
		model = requestLogic.analyze_post(model, ad);
		
		return "analyze";
	}
	@RequestMapping(value =  {"/user"})
	public String user(Model model, @RequestParam(value = "ID", required = false)String ID, @RequestParam(value = "IDbef", required = false)String IDbef) {
		if(ID==null)ID="";
		if(IDbef!=null)ID = ID+" "+IDbef;
		model = requestLogic.user_get(model, ID);
		return "user";
	}
}