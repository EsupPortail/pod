(function() {
	'use strict';
	var videojs = null;
	if(typeof window.videojs === 'undefined' && typeof require === 'function') {
		videojs = require('video.js');
	} else {
		videojs = window.videojs;
	}

	(function(window, videojs) {
		var videoJsQualityLevelPlayer,
			defaults = {
				ui: true,
				default: 'auto'
			};

		/*
		 * Quality menu item
		 *
		 */
		var MenuItem = videojs.getComponent('MenuItem');
		var QualityMenuItem = videojs.extend(MenuItem, {
			constructor: function(player, options){
				options.selectable = true;
				MenuItem.call(this, player, options);
				this.src = options.src;

				player.on('qualitychange', videojs.bind(this, this.update));
			}
		});
		QualityMenuItem.prototype.handleClick = function(event){
			MenuItem.prototype.handleClick.call(this, event);
			this.player_.currentResolution(this.options_.label);
		};
		QualityMenuItem.prototype.update = function(){
			var selection = this.player_.currentResolution();
			this.selected(this.options_.label === selection.label);
		};
		MenuItem.registerComponent('QualityMenuItem', QualityMenuItem);

		/*
		 * Quality menu button title
		 */
		var QualityTitleMenuItem = videojs.extend(MenuItem, {
			constructor: function(player, options) {
				MenuItem.call(this, player, options);
				this.off('click');
			}
		});
		MenuItem.registerComponent('QualityTitleMenuItem', QualityTitleMenuItem);

		/*
		 * Quality menu button
		 */
		var MenuButton = videojs.getComponent('MenuButton');
		var QualityMenuButton = videojs.extend(MenuButton, {
			constructor: function(player, options){
				this.label = document.createElement('span');
				options.label = 'Quality';
				MenuButton.call(this, player, options);
				this.el().setAttribute('aria-label', 'Quality');
				videojs.dom.addClass(this.el(), 'vjs-quality-button');
				this.controlText('Quality');

				if(options.dynamicLabel){
					videojs.dom.addClass(this.label, 'vjs-quality-button-label');
					this.el().appendChild(this.label);
				} else {
					var staticLabel = document.createElement('span');
					videojs.dom.addClass(staticLabel, 'vjs-menu-icon');
					this.el().appendChild(staticLabel);
				}
				player.on('updateSources', videojs.bind(this, this.update));
			}
		});
		QualityMenuButton.prototype.createItems = function(){
			var menuItems = [];
			var labels = (this.sources && this.sources.label) || {};

			// Add the menu title item
			menuItems.push(new QualityTitleMenuItem(this.player_, {
				el: videojs.dom.createEl('li', {
				  className: 'vjs-menu-title vjs-chap-menu-title',
				  innerHTML: 'Quality'
				})
			}));

			// FIXME order is not guaranteed here.
			for (var key in labels) {
				if (labels.hasOwnProperty(key)) {
				  menuItems.push(new QualityMenuItem(
				    this.player_,
				    {
				      label: key,
				      src: labels[key],
				      selected: key === (this.currentSelection ? this.currentSelection.label : false)
				    })
				  );
				}
			}
			return menuItems;
		};
		QualityMenuButton.prototype.update = function(){
			this.sources = this.player_.getGroupedSrc();
			this.currentSelection = this.player_.currentResolution();
			this.label.innerHTML = this.currentSelection ? this.currentSelection.label : '';
			return MenuButton.prototype.update.call(this);
		};
		QualityMenuButton.prototype.buildCSSClass = function(){
			return MenuButton.prototype.buildCSSClass.call(this) + ' vjs-quality-button';
		};
		MenuButton.registerComponent('QualityMenuButton', QualityMenuButton);

		/**
		 * Initialize the plugin.
		 *
		 */
		videoJsQualityLevelPlayer = function(options) {
			var settings = videojs.mergeOptions(defaults, options),
				player = this,
				groupedSrc = {},
				currentSources = {},
				currentResolutionState = {};

			/**
			 * Updates player sources or returns current source URL
			 */
			player.updateSrc = function(src){
				if(!src){ return player.src(); }

				this.currentSources = src.sort(compareResolutions);
				this.groupedSrc = bucketSources(this.currentSources);

				var chosen = chooseSrc(this.groupedSrc, this.currentSources);
				this.currentResolutionState = {
					label: chosen.label,
					sources: chosen.sources
				};

				player.trigger('updateSources');
				player.setSourcesSanitized(chosen.sources, chosen.label);
				player.trigger('qualitychange');
				return player;
			};

			/**
			 * Returns current resolution or sets one when label is specified
			 */
			player.currentResolution = function(label){
				if(label == null) { return this.currentResolutionState; }

				if (!this.groupedSrc || !this.groupedSrc.label || !this.groupedSrc.label[label]){
					return;
				}
				var sources = this.groupedSrc.label[label];
				var currentTime = player.currentTime();
				var isPaused = player.paused();

				if (!isPaused && this.player_.bigPlayButton){
					this.player_.bigPlayButton.hide();
				} else {
					this.player_.bigPlayButton.show();
				}

				var handleSeekEvent = 'loadeddata';
				player
					.setSourcesSanitized(sources, label);
				player
					.one(handleSeekEvent, function() {
						player.currentTime(currentTime);
						player.handleTechSeeked_();
						if (!isPaused){
							player.play();
							player.handleTechSeeked_();
						}
						player.trigger('qualitychange');
					});
				return player;
			};

			/**
			 * Returns grouped sources by label, resolution and type
			 */
			player.getGroupedSrc = function(){
				return this.groupedSrc;
			};

			player.setSourcesSanitized = function(sources, label){
				this.currentResolutionState = {
					label: label,
					sources: sources
				};
					
				player.src(sources.map(function(src) {
					return {src: src.id, type: 'application/x-mpegURL', res: src.height};
				}));

				return player;
			};

			/**
			 * Method used for a sorting list of sources
			 */
			function compareResolutions(a, b){
				if(!a.height || !b.height){ return 0; }
				return (+a.height)-(+b.height);
			}


			/**
			 * Group sources by label, resolution and type (if specified)
			 */
			function bucketSources(src){
				var resolutions = {
					label: {},
					height: {},
					bitrate: {}
				};
				src.map(function(source) {
					initResolutionKey(resolutions, 'label', source);
					initResolutionKey(resolutions, 'height', source);
					initResolutionKey(resolutions, 'bitrate', source);

					appendSourceToKey(resolutions, 'label', source);
					appendSourceToKey(resolutions, 'height', source);
					appendSourceToKey(resolutions, 'bitrate', source);
				});
				return resolutions;
			}

			function initResolutionKey(resolutions, key, source) {
				if (resolutions[key][source[key]] == null) {
					resolutions[key][source[key]] = [];
				}
			}

			function appendSourceToKey(resolutions, key, source) {
				resolutions[key][source[key]].push(source);
			}


			/**
			 * Choose src if option.default is specified
			 */
			function chooseSrc(groupedSrc, src) {
				var selectedRes = settings['default'];
				var selectedLabel = '';
				var source = '';
				if (selectedRes === 'high') {
					selectedRes = src[0].height;
					selectedLabel = src[0].label;
					source = groupedSrc.height[selectedRes];
				} else if (selectedRes === 'low' || selectedRes == null || !groupedSrc.height[selectedRes]) {
					selectedRes = src[src.length - 1].height;
					selectedLabel = src[src.length -1].label;
					source = groupedSrc.height[selectedRes]
				} else if (groupedSrc.height[selectedRes]) {
					selectedLabel = groupedSrc.height[selectedRes][0].label;
					source = groupedSrc.height[selectedRes]
				}
				return {res: selectedRes, label: selectedLabel, sources: source};
			}

			player.ready(function(){
				var qualityLevels = player.qualityLevels();
				if (settings.ui && qualityLevels.length > 1) {
					var menuButton = new QualityMenuButton(player, settings);
					player.controlBar.qualityLevel = player.controlBar.el_.insertBefore(menuButton.el_, player.controlBar.getChild('fullscreenToggle').el_);
					player.controlBar.qualityLevel.dispose = function(){
						this.parentNode.removeChild(this);
					};
				}
				if (qualityLevels.length > 1){
					var sources = [];
					// Add available resolution(s)
					for (var i = 0; i < qualityLevels.length; i++) {
						var height = /(360|720|1080)/.exec(qualityLevels[i].id);
						qualityLevels[i].label = 
							height[1] + ' (' + Math.round(qualityLevels[i].bitrate / 1000) + 'kbps)';
						sources.push(qualityLevels[i]);
					}
					sources.push({
						id: $('#'+player.id()).data('m3u8'),
						label: 'auto',
						height: 1
					})
					player.updateSrc(sources);
				} else {
					player.videoJsQualityLevelPlayer();
				}
			});
		};

		videojs.registerPlugin('videoJsQualityLevelPlayer', videoJsQualityLevelPlayer);
	})(window, videojs);
})();