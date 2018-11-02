$(window).load(init());

function init() {

	// ツイート
	function tweet() {
		var data = JSON.stringify({
			"tweet": $("#text").val(),
			"media": $("#media").val()
		});
		$.ajax({
			type: "post",
			url: "/tweet",
			data: data,
			contentType: "application/json",
			success: function() {
				$("#text").val("");
				$("#media").val("");
				update("Myself");
			},
			error: function() {
				alert("Tweet failed");
			}
		});
	}

	// ツイートボタン
	$(document).on("click", "#tweet", function() {
		tweet();
		return false;
	});

	// ツイートコマンド
	$("#text").keydown(function(e) {
		if(e.ctrlKey){
			if(e.keyCode === 13){
				tweet();
				return false;
			}
		}
	});

	// ツイート削除
	$(document).on("click", "#delete", function() {
		var button = $(this);
		var data = JSON.stringify({
			"tweet_id": $(this).attr("value")
		});
		$.ajax({
			type: "post",
			url: "/delete",
			data: data,
			contentType: "application/json",
			dataType: "json",
			success: function(tweet) {
				//button.attr("class", "favorited_btn");
				button.parent().remove();
			},
			error: function() {
				alert("Delete failed");
			}
		});
	});

	// ファイル
	$(document).on("click", "#file", function() {
		var html =
			'<form id="uploadForm" style="display: none;">' +
			'<input id="theFile" name="image" type="file">' +
			'</form>';
		$("body").append(html);
		$("#theFile").on("change", uploadFile).click();
	});

	// ファイルアップロード
	var uploadFile = function () {
		var formData = new FormData($("#uploadForm")[0]);
		$.ajax({
			url: "/upload",
			type: "post",
			data: formData,
			processData: false,
			contentType: false,
			timeout: 10000
		}).then(function(name){
			$("#media").val(name);
			$("#uploadForm").remove();
		});
	};

	// ネームリスト
	var nameList = [
		"Timeline",
		"Kawaii",
		"MyList",
		"University",
		"Myself"
	];

	// アップデート
	function update(name, first = false) {
		var id = "#" + name;
		var data = JSON.stringify({
			"name": name
		});
		$.ajax({
			type: "post",
			url: "/update",
			data: data,
			contentType: "application/json",
			success: function(data) {
				var tweetList = JSON.parse(data.tweetList);
				var height = $(id).parent().scrollTop();
				$(id).prepend(data.html);
				if(first && name != "Myself")
					$(id).prepend('<hr id="line" class="line">');
				if(height <= 1)
					$(id).parent().scrollTop(1);
				else if($(id).parent().scrollTop() != height)
					$(id + " #top").css("background", "#98bcff");
				$($(id+" #content").get().reverse()).each(function(i,content) {
					if($(id).parent().get(0).scrollHeight > 5000){
						content.remove();
						return;
					}
					tweetList.forEach(function(tweet) {
						if($(content).attr("value") == tweet["id_str"]){
							$("#time", content).text(tweet["time"]);
							$("#count", content).text(tweet["favorite_count"]);
							if(tweet["favorited"]) $("#favorite", content).attr("class", "favorited_btn");
							else $("#favorite", content).attr("class", "favorite_btn");
						}
					});
				});
			}
		});
	}

	nameList.forEach(function(name) {
		var id = "#" + name;
		update(name, true);
		// トップボタン
		$(document).on("click", id + " #top", function() {
			$(this).css("background", "");
			$(id).parent().scrollTop(0);
		});
		// スクロール読み込み
		$(id).parent().scroll(function() {
			if($(this).scrollTop() == 0){
				$(id + " #top").css("background", "");
				if(name != "Myself"){
					$(id + " #line").remove();
					$(id).prepend('<hr id="line" class="line">');
				}
			}
		});
		// お気に入り
		$(document).on("click", id + " #favorite", function() {
			var button = $(this);
			var data = JSON.stringify({
				"tweet_id": $(this).attr("value")
			});
			$.ajax({
				type: "post",
				url: "/favorite",
				data: data,
				contentType: "application/json",
				dataType: "json",
				success: function(tweet) {
					button.attr("class", "favorited_btn");
					$("#count", button.parent()).text(tweet["favorite_count"]);
				},
				error: function() {
					alert("Like failed");
				}
			});
		});
		// お気に入りユーザー取得
		$(document).on("click", id + " #count", function() {
			var data = $(this).attr("value").split(",");
			data = JSON.stringify({
				"tweet_id": data[0],
				"user_id": data[1]
			});
			$.ajax({
				type: "post",
				url: "/getFavorite",
				data: data,
				contentType: "application/json",
				success: function(data) {
					var userList = JSON.parse(data);
					var message = ""
					userList.forEach(function(user) {
						message += user["name"]+" @"+user["screen_name"]+"\n"
					});
					alert(message);
				}
			});
		});
	});

	// 定期更新
	setInterval(function() { update("Timeline"); }, 120000);
	setInterval(function() { update("Kawaii"); }, 10000);
	setInterval(function() { update("MyList"); }, 30000);
	setInterval(function() { update("University"); }, 30000);
	setInterval(function() { update("Myself"); }, 30000);
}

