function NewAppTourManager (options) {
    'use strict';
    var self = this;
    self.slug = options.slug;
    self.area = options.area;
    self.domain = options.domain;
    self.furthest_step = options.furthest_step;
    self.update_url = options.update_url;
    self.base_url = options.base_url;
    self.form_home = 'modules-0/forms-0/';
    self.form_edit = 'modules-0/forms-0/source/';

    self.tour = new Tour({
        steps: [
            {
                element: '.edit-module-li[data-index="0"]',
                title: "Go here, bitches!",
                content: 'BAM',
                basePath: self.base_url,
                path: '',
                onNext: function (tour) {
                    console.log('help');
                }
            },
            {
                element: '.edit-module-li[data-index="0"]',
                title: "Another one",
                content: "BAM",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: ''
            },
            {
                element: '#edit_label',
                title: "Edit this mofo.",
                content: "YESSSS",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_home
            },
            {
                element: '.fd-question-group-Text .fd-question-type-default',
                title: "Add a new text question",
                content: "ADD IT NOW",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_edit
            },
            {
                element: '#fd-question-edit-main',
                title: "Update Question info",
                content: "FOO",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_edit
            },
            {
                element: '.fd-save-button',
                title: "save the form",
                content: "SAVE IT NOW",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_edit
            },
            {
                element: '.edit-form-li.active',
                title: "Go back to form view",
                content: "blah",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_edit
            },
            {
                element: '#cloudcare-preview-url',
                title: "Try out the form in cloudcare",
                content: "blah",
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_home
            },
            {
                element: '.sidebar .app-manager-content .nav:first-child li:first-child a',
                title: "Deploy!",
                content: 'deploy now',
                onNext: self._updateTour,
                basePath: self.base_url,
                path: self.form_home
            }
        ]
    });

    self.utils = {
        getTourAlertContainer: function () {
            return $('#tour-alert-' + self.slug);
        }
    };

    self.init = function () {
        $(function () {
            var $tourAlert = self.utils.getTourAlertContainer();
            $tourAlert.find('.tour-begin').click(function () {
                $tourAlert.addClass('hide');
                self.tour.init();
                self.tour.start();
            });
        });
    };


    self._updateTour = function (tour) {
        console.log('next');
        console.log(tour);
        $.post({
            url: self.update_url,
            data: {
                slug: self.slug,
                area: self.area,
                domain: self.domain,
                step: tour.getCurrentStep()
            },
            dataType: 'json',
            success: function (data) {
                console.log('success');
                console.log(data);
            }
        });
    };
}
