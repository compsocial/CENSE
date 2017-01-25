// don't forget to ssh tunnel
var serverUrl = "http://localhost:8000/";
var logging = true;
var keywords = [];

function log() {
	if (logging) {
		console.log.apply(console, arguments);
	}
}

var delay = (function () {
	var timer = 0;
	return function (callback, ms) {
		clearTimeout(timer);
		timer = setTimeout(callback, ms);
	}
})();

/**
 * load censored keywords
 **/
function loadKeywords() {
	$.getJSON(serverUrl + "keywords", function (data) {
		keywords = data;
		log("keywords = ", keywords)
	});
}
loadKeywords();

$(document).ready(function () {
	log("ready");

	/**
	 * inject modal
	 **/
	$.get(chrome.extension.getURL("/modal.html"), function(data) {
		$(data).appendTo("div#v6_pl_content_publishertop");

		// when the user clicks on (x), close the modal
		$("#suggestionModal .close").click(function() {
			log("close click");
			$("#suggestionModal div.modal-content").slideUp(400);
		});

		// user accept suggestion
		$("#suggestionModal button#accept-suggestion").click(function () {
			log("accept click");
			// var suggestionPost = $("div#suggestionModal td#suggestion-post").text();
			var suggestionPost = $("div#suggestionModal textarea#textarea-suggestion-post ~ pre").text();
			console.log(suggestionPost);
			$("div#v6_pl_content_publishertop textarea").val(suggestionPost);
			$("#suggestionModal .close").click();
			getSuggestionForCensoredKeywords();
		});

		// user wants new suggestion
		$("#suggestionModal button#new-suggestion").click(function () {
			log("new suggestion click");
			getSuggestionForCensoredKeywords();
		});

		// user cancel suggestion
		$("#suggestionModal a#cancel-suggestion").click(function () {
			log("cancel click");
			$("#suggestionModal .close").click();
		});

		getSuggestionForCensoredKeywords();
		
		log("modal injected");
	});

	/**
	 * add event listener to status update box
	 **/
	$("<style type='text/css'> " + 
		".redbutton { background-image: url('" + chrome.extension.getURL("img/red_light.png") + "'); background-size: 100%; background-repeat: no-repeat; } " + 
		".redbutton:hover { background-image: url('" + chrome.extension.getURL("img/red_expand.png") + "'); background-size: 100%; background-repeat: no-repeat; } " + 
		".greenbutton { background-image: url('" + chrome.extension.getURL("img/green_light.png") + "'); background-size: 100%; background-repeat: no-repeat; } " + 
		".loadingbutton { background-image: url('" + chrome.extension.getURL("img/loading.gif") + "'); background-size: 100%; background-repeat: no-repeat; } " + 
		"</style>"
	).appendTo("head");

	var red_button = $("<div id='redbutton' class='textareabutton clickablebutton redbutton' title='Your post might be censored! Click to see suggestion.'></div>");
	red_button.insertAfter($("div#v6_pl_content_publishertop textarea"));
	red_button.click(function() {
		$("div.modal-content").slideDown(500);
	});
	red_button.tooltip();

	var green_button = $("<div id='greenbutton' class='textareabutton greenbutton' title='No censored keywords detected.'></div>");
	green_button.insertAfter(red_button);
	green_button.tooltip();

	var loading_button = $("<div id='loadingbutton' class='textareabutton loadingbutton' title='Loading...'></div>");
	loading_button.insertAfter(green_button);
	loading_button.tooltip();
	
	function getSuggestionForCensoredKeywords() {
		var currentTextValue = $("div#v6_pl_content_publishertop textarea").val();
		if (!currentTextValue || currentTextValue.length == 0) {
			log("no status update yet");
			red_button.hide();
			green_button.hide();
			loading_button.hide();
			return;
		}

		log(currentTextValue);

		var keywordIndices = [];
		$.each(keywords, function (index, keyword) {
			var keywordIndex = currentTextValue.indexOf(keyword);
			while (keywordIndex >= 0) {
				keywordIndices.push([keywordIndex, keyword]);
				keywordIndex = currentTextValue.indexOf(keyword, keywordIndex + keyword.length);
			}
		});

		if (keywordIndices.length > 0) {
			// show red light that's clickable to suggestions
			log(keywordIndices);
			keywordIndices.sort(function (a, b) {
				return a[0] - b[0];
			});
			log("sorted", keywordIndices);

			var highlightedHTML = "";
			
			var censoredKeywords = "";
			var startIndex = 0;
			for (var i = 0; i < keywordIndices.length; i++) {
				var wordIndex = keywordIndices[i][0];
				var word = keywordIndices[i][1];
				highlightedHTML = highlightedHTML + currentTextValue.substring(startIndex, wordIndex) +
					"<span class='highlight'>" + word + "</span>";
				startIndex = wordIndex + word.length;
				censoredKeywords = censoredKeywords + word + ",";
			}
			if (censoredKeywords.length > 0) {
				censoredKeywords = censoredKeywords.substring(0, censoredKeywords.length - 1);
			}
			var url = serverUrl + "homophone?keyword=" + encodeURIComponent(censoredKeywords);
			log(url);
			$.getJSON(url, function (data) {
				var replacements = data;
				log(replacements);
				var suggestionText = "";
				var suggestionWords = []
				var startIndex = 0;
				for (var i = 0; i < keywordIndices.length; i++) {
					var wordIndex = keywordIndices[i][0];
					var word = keywordIndices[i][1];
					var replacement = replacements[i];
					log(replacement);
					suggestionText = suggestionText + currentTextValue.substring(startIndex, wordIndex) + replacement;
					// suggestionHTML = suggestionHTML + currentTextValue.substring(startIndex, wordIndex) +
					// 	"<span class='highlight'>" + replacement + "</span>";
					startIndex = wordIndex + word.length;
					suggestionWords.push(replacement);
				}
				// suggestionHTML = suggestionHTML + currentTextValue.substring(startIndex, currentTextValue.length);
				suggestionText = suggestionText + currentTextValue.substring(startIndex, currentTextValue.length);

				log("suggestionWords = ", suggestionWords);
				$("div#suggestionModal textarea#textarea-suggestion-post").remove();
				$("<textarea id='textarea-suggestion-post'></textarea>").appendTo("div#suggestionModal td#suggestion-post");
				// $("div#suggestionModal textarea#textarea-suggestion-post").trigger('textarea.highlighter.destroy');
				$("div#suggestionModal textarea#textarea-suggestion-post").textareaHighlighter({
					matches: [
						{
							"match": suggestionWords,
							"matchClass": "highlight"
						}
					]
				});
				$("div#suggestionModal textarea#textarea-suggestion-post").text(suggestionText).trigger('input.textarea.highlighter');
				// $("div#suggestionModal textarea#textarea-suggestion-post ~ pre").text(suggestionText);
				// $("div#suggestionModal td#suggestion-post").html(suggestionHTML);
			});
			highlightedHTML = highlightedHTML + currentTextValue.substring(startIndex, currentTextValue.length);
			$("div#suggestionModal td#user-post").html(highlightedHTML);
			green_button.hide();
			loading_button.hide();
			red_button.show();
		}
		else {
			// show green light with tooltip that says the post is cleared
			red_button.hide();
			loading_button.hide();
			green_button.show();
		}
	}
	function checkTextForCensoredKeywords() {
		// TODO: show some kind of feedback, spinning icon
		// remove any previous indicator (red light/green light)
		loading_button.show();
		red_button.hide();
		$("#suggestionModal div.modal-content").slideUp();
		green_button.hide();

		// delay the checking to wait for the user to finish typing
		delay(getSuggestionForCensoredKeywords, 500);
	}

	$("div#v6_pl_content_publishertop textarea").on("keyup paste", checkTextForCensoredKeywords);
	$("div#v6_pl_content_publishertop textarea").on("change", function () {
		// check if red button is visible if so, don't check the text
		if ($("#redbutton").is(":visible")) {
			$("#redbutton").click();
		}
		else if ($("#greenbutton").is(":visible")) {
			log("green button is visible");
		}
		else {
			checkTextForCensoredKeywords();
		}
	});

	log("loaded");
});