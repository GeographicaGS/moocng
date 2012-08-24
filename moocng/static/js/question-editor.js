/*jslint browser: true, nomen: true */
/*global MOOC: true, Backbone, jQuery, _ */

(function ($, Backbone, _) {
    "use strict";

    if (_.isUndefined(window.MOOC)) {
        window.MOOC = {};
    }

    MOOC.models = {};

    MOOC.models.Option = Backbone.Model.extend({
        defaults: function () {
            return {
                optiontype: 't',
                x: 0,
                y: 0,
                width: 100,
                height: 12,
                solution: ''
            };
        }
    });

    MOOC.models.OptionList  = Backbone.Collection.extend({
        model: MOOC.models.Option
    });

    MOOC.views = {};

    MOOC.views.OptionView = Backbone.View.extend({
        tagName: 'span',
        className: 'option',
        padding: 5,
        option_types: {
            't': 'text',
            'c': 'checkbox',
            'r': 'radio'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'drag', 'start', 'stop',
                      'select', 'unselect', 'is_out', 'change');
            this.model.bind("change", this.render, this);

            this.parent_view = this.options.parent_view;
            this.parent_width = this.options.parent_width;
            this.parent_height = this.options.parent_height;
        },

        render: function () {
            var optiontype = this.model.get('optiontype'), attributes = {
                type: this.option_types[optiontype],
                value: this.model.get('solution'),
                style: [
                    "width: " + this.model.get("width") + "px;",
                    "height: " + this.model.get("height") + "px;"
                ].join(" ")
            };
            if (optiontype === 'c' || optiontype === 'r') {
                if (this.model.get('solution') === 'True') {
                    attributes.checked = 'checked';
                }
            } else {
                attributes.value = this.model.get('solution');
            }

            this.$el.empty().append(this.make("input", attributes));
            this.$el
                .width(this.model.get("width") + this.padding * 2)
                .height(this.model.get("height") + this.padding * 2)
                .css({
                    left: (this.model.get('x') - this.padding) + "px",
                    top: (this.model.get('y') - this.padding) + "px",
                    padding: this.padding + "px",
                    position: 'absolute'
                })
                .draggable({
                    drag: this.drag,
                    start: this.start,
                    stop: this.stop
                })
                .find('input').change(this.change);

            return this;
        },

        is_out: function (position) {
            return ((position.left + this.padding) < 0
                    || (position.top + this.padding) < 0
                    || (position.left + this.padding) > this.parent_width
                    || (position.top + this.padding) > this.parent_height);
        },

        drag: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.$el.addClass('out');
            } else {
                this.model.set("x", position.left + this.padding);
                this.model.set("y", position.top + this.padding);
                this.$el.removeClass('out');
            }
        },

        start: function () {
            this.parent_view.select_option(this.el);
        },

        stop: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.model.unbind("change", this.render);
                this.model.destroy();
                MOOC.router.navigate("", {trigger: true});
            } else {
                this.model.set("x", position.left + this.padding);
                this.model.set("y", position.top + this.padding);
                this.model.save();
            }
        },

        select: function () {
            this.$el.addClass('selected');
        },

        unselect: function () {
            this.$el.removeClass('selected');
        },

        change: function () {
            var $input = this.$el.find('input'),
                optiontype = this.model.get('optiontype'),
                value = '';
            if (optiontype === 'c' || optiontype === 'r') {
                value = _.isUndefined($input.attr('checked')) ? false : true;
            } else {
                value = $input.val();
            }
            this.model.set("solution", value);
            this.model.save();
        }

    });

    MOOC.views.OptionPropertiesView = Backbone.View.extend({
        events: {
            "click #remove-option": "remove_option"
        },

        initialize: function () {
            _.bindAll(this, 'close', 'render', 'reset', 'remove_option',
                      'change_solution', 'change_type',
                      'change_x', 'change_y', 'change_width', 'change_height',
                      '_change_property');
            this.model.bind("change", this.render, this);
        },

        close: function () {
            this.model.unbind("change", this.render);
            this.unbind();
            this.$el.find("#option-optiontype").unbind('change');
            this.$el.find("#option-solution").unbind('change');
            this.$el.find("#option-x").unbind('change');
            this.$el.find("#option-y").unbind('change');
            this.$el.find("#option-width").unbind('change');
            this.$el.find("#option-height").unbind('change');
        },

        render: function () {
            this.$el
                .find('#option-id').html(this.model.get('id')).end()
                .find('#option-optiontype').change(this.change_type).val(this.model.get('optiontype')).end()
                .find('#option-solution').change(this.change_solution).val(this.model.get('solution')).end()
                .find('#option-x').change(this.change_x).val(this.model.get('x')).end()
                .find('#option-y').change(this.change_y).val(this.model.get('y')).end()
                .find('#option-width').change(this.change_width).val(this.model.get('width')).end()
                .find('#option-height').change(this.change_height).val(this.model.get('height'));
        },

        change_type: function () {
            this._change_property('optiontype', false);
        },

        change_solution: function () {
            this._change_property('solution', false);
        },

        change_x: function () {
            this._change_property('x', true);
        },

        change_y: function () {
            this._change_property('y', true);
        },

        change_width: function () {
            this._change_property('width', true);
        },

        change_height: function () {
            this._change_property('height', true);
        },

        remove_option: function () {
            this.model.destroy();
            MOOC.router.navigate("", {trigger: true});
        },

        reset: function () {
            this.$el
                .find('#option-id').html('').end()
                .find('#option-optiontype').val('').end()
                .find('#option-solution').val('').end()
                .find('#option-x').val('').end()
                .find('#option-y').val('').end()
                .find('#option-width').val('').end()
                .find('#option-height').val('');
        },

        _change_property: function (prop, numerical) {
            var value = this.$el.find("#option-" + prop).val();
            if (value) {
                if (numerical) {
                    value = parseInt(value, 10);
                }
                this.model.set(prop, value);
                this.model.save();
            }
        }

    });

    // In this variable we store the current properties view
    // so we can clean up stuff when we switch the view
    MOOC.views.current_properties_view = null;

    MOOC.views.Index = Backbone.View.extend({
        events: {
            "click #add-option": "create_option",
            "click fieldset span ": "option_click",
            "click fieldset span input": "option_click"
        },

        initialize: function () {
            var $img, url, width, height;

            _.bindAll(this, 'render', 'add', 'remove',
                      'create_option', 'select_option', 'option_click');

            this.$fieldset = this.$el.find("fieldset");

            // internal state
            this._rendered = false;

            // create an array of option views to keep track of children
            this._optionViews = [];

            // add each option to the view
            this.collection.each(this.add);

            // bind this view to the add and remove events of the collection
            this.collection.bind("add", this.add);
            this.collection.bind("remove", this.remove);
        },

        render: function () {
            var self = this;
            this._rendered = true;

            this.$fieldset.empty();
            _(this._optionViews).each(function (ov) {
                self.$fieldset.append(ov.render().el);
            });

            return this;
        },

        add: function (option) {
            var ov = new MOOC.views.OptionView({
                model: option,
                parent_view: this,
                parent_width: this.$fieldset.width(),
                parent_height: this.$fieldset.height()
            });
            this._optionViews.push(ov);

            if (this._rendered) {
                this.$fieldset.append(ov.render().el);
            }
        },

        remove: function (option) {
            var view_to_remove = _(this._optionViews).select(function (ov) {
                return ov.model === option;
            })[0];
            this._optionViews = _(this._optionViews).without(view_to_remove);

            if (this._rendered) {
                view_to_remove.remove();
            }
        },

        create_option: function () {
            var option = new MOOC.models.Option({
                optiontype: this.$el.find("#option-optiontype-creation").val()
            });
            this.collection.add(option);
            option.save();
        },

        select_option: function (option_element) {
            var selected = null;
            _(this._optionViews).each(function (ov) {
                if (ov.el === option_element) {
                    ov.select();
                    selected = ov;
                } else {
                    ov.unselect();
                }
            });
            if (selected !== null) {
                MOOC.router.navigate("option" + selected.model.get('id'),
                                     {trigger: true});
            }
        },

        option_click: function (event) {
            var target = event.target;
            if (target.tagName === 'INPUT') {
                target = target.parentNode;
            }
            this.select_option(target);
        }
    });

    MOOC.views.current_index_view = null;

    MOOC.App = Backbone.Router.extend({
        index: function () {
            if (MOOC.views.current_index_view === null) {
                MOOC.views.current_index_view = new MOOC.views.Index({
                    collection: MOOC.models.options,
                    el: $("#content-main")[0]
                });
            }

            MOOC.views.current_index_view.render();

            if (MOOC.views.current_properties_view !== null) {
                MOOC.views.current_properties_view.close();
                MOOC.views.current_properties_view.reset();
                MOOC.views.current_properties_view = null;
            }
        },

        option: function (opt) {
            var view = new MOOC.views.OptionPropertiesView({
                model: MOOC.models.options.get(parseInt(opt, 10)),
                el: $("#option-properties")[0]
            });

            if (MOOC.views.current_properties_view !== null) {
                MOOC.views.current_properties_view.close();
            }

            MOOC.views.current_properties_view = view;
            MOOC.views.current_properties_view.render();
        }
    });

    MOOC.init = function (url, options) {
        var path = window.location.pathname;
        MOOC.models.options = new MOOC.models.OptionList();
        MOOC.models.options.reset(options);
        MOOC.models.options.url = url;

        // Put the img as a background image of the fieldset
        (function () {
            var $fieldset = $("#content-main fieldset"),
                $img = $fieldset.find("img"),
                url = $img.attr("src"),
                width = $img.width(),
                height = $img.height();
            $fieldset.width(width).height(height).css({"background-image": "url(" + url + ")"});
            $img.remove();
        }());

        MOOC.router = new MOOC.App();
        MOOC.router.route("", "index");
        MOOC.router.route("option:option", "option");
        Backbone.history.start({root: path});

        MOOC.router.navigate("", {trigger: true});
    };
}(jQuery, Backbone, _));