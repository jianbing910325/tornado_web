$(function(){
	/* 增 */
		$("#hgc_submit").click(function(){
			if (!$("#hgc_name").val()){
					alert("请输入主机组名!!!");
					return false;
			}
			$.post("/zabbix/hostgroup/create",
				{params: jQuery.toJSON({name: $("#hgc_name").val()}), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机组: "+$("#hgc_name").val()+"创建成功,主机组ID: "+obj.groupids);
					}
			})
		});
		
		$("#tc_submit").click(function(){
			if (!$("#tc_hostgroupid").val() || !$("#tc_name").val()){
				alert("模板名和主机组ID是必填项,需要填写!");
				return false;
			}
			
			var hostgroups = $("#tc_hostgroupid").val().split(",");
			var host = new Array();
			var hostgroup = new Array();
			for (var i=0; i<hostgroups.length; i++){
					hostgroup.push({"groupid": hostgroups[i]});
			}
			var thing = {"host": $("#tc_name").val(),
						 "groups": hostgroup};
			if ($("#tc_hostid").val()){
				var hosts = $("#tc_hostid").val().split(",");
				for (var i=0; i<hosts.length; i++){
					host.push({"hostid": hosts[i]});
				}
				thing["hosts"] = host;
			}
			$.post("/zabbix/template/create",
				{params: jQuery.toJSON(thing), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("模板:"+$("#tc_name").val()+"创建成功,模板ID: "+obj.templateids);
					}
			})
		});
		
		$("#hc_submit").click(function(){
			if (!$("#hc_host").val() || !$("#hc_name").val() || !$("#hc_hostgroupid").val()) {
				alert("主机IP,主机名,主机组ID都为必填项，请填写!");
				return false;
			}
			
			var hostgroups = $("#hc_hostgroupid").val().split(",");
			
			var template = new Array();
			var hostgroup = new Array();
			
			for (var i=0; i<hostgroups.length; i++){
				hostgroup.push({"groupid": hostgroups[i]});
			}
			
			var thing = {"host": $("#hc_host").val(),
						 "name": $("#hc_name").val(),
						 "interfaces": [{"type": 1,
										 "main": 1,
										 "useip": 1,
										 "ip": $("#hc_host").val(),
										 "dns": "",
										 "port": "10050"
										 }],
						 "groups": hostgroup
					};
					
			if ($("#hc_templateid").val()){
				var templates = $("#hc_templateid").val().split(",");
				for (var i=0; i<templates.length; i++){
					template.push({"templateid": templates[i]});
				}
				thing["templates"] = template;
			}
			$.post("/zabbix/host/create",
				{params: jQuery.toJSON(thing), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机:"+$("#hc_name").val()+"创建成功,主机IP:"+$("#hc_host").val()+" 主机ID: "+obj.hostids);
					}
			})
		});
		
		/* 删 */
		$("#hgd_submit").click(function(){
			if (!$("#hgd_id").val()){
				alert("请输入需要删除的主机组ID!!!");
				return false;
			}
			var hostgroups = $("#hgd_id").val().split(",");
			$.post("/zabbix/hostgroup/delete",
				{params: jQuery.toJSON(hostgroups), time: new Date()},
				function(msg){
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机组: ID为"+obj.groupids+"成功删除.");
					}
			});
		});
		
		$("#td_submit").click(function(){
			if (!$("#td_id").val()){
				alert("请输入需要删除的模板ID!!!");
				return false;
			}
			var templates = $("#td_id").val().split(",");
			$.post("/zabbix/template/delete",
				{params: jQuery.toJSON(templates), time: new Date()},
				function(msg){
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("模板: ID为"+obj.templateids+"成功删除.");
					}
			});
		});
		
		$("#hd_submit").click(function(){
			if (!$("#hd_id").val()){
				alert("请输入需要删除的主机ID!!!");
				return false;
			}
			var hosts = $("#hd_id").val().split(",");
			$.post("/zabbix/host/delete",
				{params: jQuery.toJSON(hosts), time: new Date()},
				function(msg){
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机: ID为"+obj.hostids+"成功删除.");
					}
			});
		});
		
		/* 改 */
		$("#hgu_submit").click(function(){
			if (!$("#hgu_name").val() || !$("#hgu_id").val()){
				alert("主机组ID、主机组名不能为空!!!");
				return false;
			}
			var thing = {groupid: $("#hgu_id").val(), name: $("#hgu_name").val()};
			$.post("/zabbix/hostgroup/update",
				{params: jQuery.toJSON(thing), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机组: ID为"+obj.groupids+"的主机组的组名修改为:"+$("#hgu_name").val());
					}
			});
		});
		
		$("#tu_submit").click(function(){
			if (!$("#tu_host").val() || !$("#tu_id").val()){
				alert("模板ID、模板名不能为空!!!");
				return false;
			}
			var thing = {"templateid": $("#tu_id").val(), "host": $("#tu_host").val()};
			if ($("#tu_name").val()){
				thing["name"] = $("#tu_name").val();
			}
			if ($("#tu_description").val()){
				thing["description"] = $("#tu_description").val();
			}
			$.post("/zabbix/template/update",
				{params: jQuery.toJSON(thing), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("模板: ID为"+obj.templateids+"的模板的模板名修改为:"+$("#tu_name").val());
					}
			});
		});
		
		$("#hu_submit").click(function(){
			if (!( $("#hu_id").val() && ( $("#hu_hostgroups").val() || $("#hu_templates").val() || $("#hu_templates_clear").val() || $("#hu_status").val() ))){
				alert("除填写主机ID外,其他必填写一项作为处理!!!");
				return false;
			}
			
			var thing = {"hostid": $("#hu_id").val()};
			if ($("#hu_hostgroups").val()){
				var hostgroups = $("#hu_hostgroups").val().split(",");
				var hostgroup = new Array();
				for (var i=0; i<hostgroups.length; i++){
					hostgroup.push({"groupid": hostgroups[i]});
				}
				thing["groups"] = hostgroup;
			}
			if ($("#hu_templates").val()){
				var templates = $("#hu_templates").val().split(",");
				var template = new Array();
				for (var i=0; i<templates.length; i++){
					template.push({"templateid": templates[i]});
				}
				thing["templates"] = template;
			}
			if ($("#hu_templates_clear").val()){
				var templates_clear = $("#hu_templates_clear").val().split(",");
				var template_clear = new Array();
				for (var i=0; i<templates_clear.length; i++){
					template_clear.push({"templateid": templates_clear[i]});
				}
				thing["templates_clear"] = template_clear;
			}
			if ($("#hu_status").val()){
				thing["status"] = $("#hu_status").val();
			}
			alert(jQuery.toJSON(thing));
			$.post("/zabbix/host/update",
				{params: jQuery.toJSON(thing), time: new Date()},
				function(msg) {
					var obj = jQuery.parseJSON(msg);
					if ( typeof obj == 'string' ){
						alert(obj);
					}else{
						alert("主机: ID为"+obj.hostids+"更改成功.");
					}
			}); 			
		});
		
		/* 查 */
		$("#hostgroupget").click(function(){
			$("#hostgroupgetdiv").show();
			$("#hostgroupgetpre").hide();
			$.post("/zabbix/hostgroup/get",
				{params: '{"output": "extend"}', time: new Date()},
				function(msg) {
					$("#hostgroupgetdiv").hide();
					$("#hostgroupgetpre").show();
					var txt = "";
					var obj = jQuery.parseJSON(msg);
					$.each(obj,function(idx,item){
						txt += "<tr><td>" + item.groupid + "</td><td>" + item.name + "</td></tr>";
						$("#echogroup").html(txt);	
					});
			});
		});
		
		$("#templateget").click(function(){
			$("#templategetdiv").show();
			$("#templategetpre").hide();
			$.post("/zabbix/template/get",
				{params: '{"output": "extend"}', time: new Date()},
				function(msg) {
					$("#templategetdiv").hide();
					$("#templategetpre").show();
					var txt = "";
					var obj = jQuery.parseJSON(msg);
					$.each(obj,function(idx,item){
						txt += "<tr><td>" + item.templateid + "</td><td>" + item.host + "</td><td>" + item.name + "</td><td>" + item.description + "</td></tr>";
						$("#echotemplate").html(txt);	
					});
			});
			
		});
		
		$("#hostget").click(function(){
			$("#hostgetdiv").show();
			$("#hostgetpre").hide();
			$.post("/zabbix/host/get",
				{params: '{"output": "extend"}',time: new Date()},
				function(msg) {
					$("#hostgetdiv").hide();
					$("#hostgetpre").show();
					var txt = "";
					var obj = jQuery.parseJSON(msg);
					$.each(obj,function(idx,item){
						txt += "<tr><td>" + item.hostid + "</td><td>" + item.host + "</td><td>" + item.name + "</td><td>" + item.status + "</td><td>" + item.available + "</td></tr>";
						$("#echohost").html(txt);	
					});
			});
		});
});