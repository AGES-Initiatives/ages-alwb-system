	$(function () {
	
		$("#dcs_tree li").each(function() {
			if ( $(this).children('ul').length > 0) {
				$(this).addClass('treeparent');
			} else {
				
				var na_patt = /NA.pdf$/i;
				if (na_patt.test($(this).attr('dcslink'))) {
					$(this).addClass('notavailable');
				}
	
				dcs_link = ($(this).attr('dcslink')) ? $(this).attr('dcslink') : "#";
				dcs_html = $(this).html(); 
	
				var pdf_patt = /.pdf/i;
				var mp3_patt = /.mp3/i;
				var html_patt = /.html/i;
				var p_patt = /p\//i;

				if (mp3_patt.test($(this).attr('dcslink'))) {
					dcs_target = "FrameAudio";
				} else if (p_patt.test( $(this).attr('dcslink'))) {
					dcs_target = "FrameScore";
				} else if (pdf_patt.test($(this).attr('dcslink'))) {
					dcs_target = "FrameScore";
				} else if (html_patt.test($(this).attr('dcslink'))) {
					dcs_target = "FrameText";
				} else {
					dcs_target = "_blank";
				}
				$(this).html("<a href='"+dcs_link+"' target='"+dcs_target+"'>" + dcs_html + "</a>");
				$(this).click(function(event) {
					event.stopPropagation();
				});
				
			}
		});
	
		$('#dcs_tree .treeparent').click(function(event) {
			event.stopPropagation();
			$(this).children('ul').toggle();
		});
	
		$("#dcs_tree .treeparent").children().toggle();
	
	});
	
