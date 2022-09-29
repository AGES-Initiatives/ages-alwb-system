/*
 * jQuery jqmdropdown: A simple jqmdropdown plugin
 *
 * Copyright 2013 Cory LaViska for A Beautiful Site, LLC. (http://abeautifulsite.net/)
 *
 * Licensed under the MIT license: http://opensource.org/licenses/MIT
 *
*/
if (jQuery) (function ($) {

    $.extend($.fn, {
        jqmdropdown: function (method, data) {

            switch (method) {
                case 'show':
                    show(null, $(this));
                    return $(this);
                case 'hide':
                    hide();
                    return $(this);
                case 'attach':
                    return $(this).attr('data-jqm-dropdown', data);
                case 'detach':
                    hide();
                    return $(this).removeAttr('data-jqm-dropdown');
                case 'disable':
                    return $(this).addClass('jqm-dropdown-disabled');
                case 'enable':
                    hide();
                    return $(this).removeClass('jqm-dropdown-disabled');
            }

        }
    });

    function show(event, object) {

        var trigger = event ? $(this) : object,
			jqmdropdown = $(trigger.attr('data-jqm-dropdown')),
			isOpen = trigger.hasClass('jqm-dropdown-open');

        // In some cases we don't want to show it
        if (event) {
            if ($(event.target).hasClass('jqm-dropdown-ignore')) return;

            event.preventDefault();
            event.stopPropagation();
        } else {
            if (trigger !== object.target && $(object.target).hasClass('jqm-dropdown-ignore')) return;
        }
        hide();

        if (isOpen || trigger.hasClass('jqm-dropdown-disabled')) return;

        // Show it
        trigger.addClass('jqm-dropdown-open');
        jqmdropdown
			.data('jqm-dropdown-trigger', trigger)
			.show();

        // Position it
        position();

        // Trigger the show callback
        jqmdropdown
			.trigger('show', {
				jqmdropdown: jqmdropdown,
				trigger: trigger
			});

    }

    function hide(event) {

        // In some cases we don't hide them
        var targetGroup = event ? $(event.target).parents().addBack() : null;

        // Are we clicking anywhere in a jqmdropdown?
        if (targetGroup && targetGroup.is('.jqm-dropdown')) {
            // Is it a jqmdropdown menu?
            if (targetGroup.is('.jqm-dropdown-menu')) {
                // Did we click on an option? If so close it.
                if (!targetGroup.is('A')) return;
            } else {
                // Nope, it's a panel. Leave it open.
                return;
            }
        }

        // Hide any jqmdropdown that may be showing
        $(document).find('.jqm-dropdown:visible').each(function () {
            var jqmdropdown = $(this);
            jqmdropdown
				.hide()
				.removeData('jqm-dropdown-trigger')
				.trigger('hide', { jqmdropdown: jqmdropdown });
        });

        // Remove all jqmdropdown-open classes
        $(document).find('.jqm-dropdown-open').removeClass('jqm-dropdown-open');

    }

    function position() {

        var jqmdropdown = $('.jqm-dropdown:visible').eq(0),
			trigger = jqmdropdown.data('jqm-dropdown-trigger'),
			hOffset = trigger ? parseInt(trigger.attr('data-horizontal-offset') || 0, 10) : null,
			vOffset = trigger ? parseInt(trigger.attr('data-vertical-offset') || 0, 10) : null;

        if (jqmdropdown.length === 0 || !trigger) return;

        // Position the jqmdropdown relative-to-parent...
        if (jqmdropdown.hasClass('jqm-dropdown-relative')) {
            jqmdropdown.css({
                left: jqmdropdown.hasClass('jqm-dropdown-anchor-right') ?
					trigger.position().left - (jqm-dropdown.outerWidth(true) - trigger.outerWidth(true)) - parseInt(trigger.css('margin-right'), 10) + hOffset :
					trigger.position().left + parseInt(trigger.css('margin-left'), 10) + hOffset,
                top: trigger.position().top + trigger.outerHeight(true) - parseInt(trigger.css('margin-top'), 10) + vOffset
            });
        } else {
            // ...or relative to document
            jqmdropdown.css({
                left: jqmdropdown.hasClass('jqm-dropdown-anchor-right') ?
					trigger.offset().left - (jqmdropdown.outerWidth() - trigger.outerWidth()) + hOffset : trigger.offset().left + hOffset,
                top: trigger.offset().top + trigger.outerHeight() + vOffset
            });
        }
    }

    $(document).on('click.jqmdropdown', '[data-jqm-dropdown]', show);
    $(document).on('click.jqmdropdown', hide);
    $(window).on('resize', position);

})(jQuery);