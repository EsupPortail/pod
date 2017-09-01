/*
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure. 
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
*/

(function() {
	'use-strict';
	var videojs = null;
	if(typeof window.videojs === 'undefined' && typeof require === 'function') {
		videojs = require('video.js');
	} else {
		videojs = window.videojs;
	}
	var list_chap = {};
	/***********************************************************************************
	 * Define some helper functions
	 ***********************************************************************************/
	 var methods = {
			/**
			 * Utility function for merging 2 objects recursively. It treats
			 * arrays like plain objects and it relies on a for...in loop which will
			 * break if the Object prototype is messed with.
			 *
			 * @param	(object)	destination	The object to modify and return
			 * @param	(object)	source		The object to use to overwrite the first
			 * 									object
			 *
			 * @returns	(object)	The modified first object is returned
			 */
			 extend : function(destination, source) {
			 	for (var prop in source) {
			 		if (typeof source[prop] == 'object' && null !== source[prop]) {
			 			destination[prop] = methods.extend(destination[prop] || {}, source[prop]);
			 		} else {
			 			destination[prop] = source[prop];
			 		}
			 	}

			 	return destination;
			 },

			/**
			 * In a future version, this can be made more intelligent,
			 * but for now, we'll just add a "p" at the end if we are passed
			 * numbers.
			 *
			 * @param	(string)	res	The resolution to make a label for
			 *
			 * @returns	(string)	The label text string
			 */
			 chap_label : function(chap) {
			 	return list_chap[chap];
			 }
			};

	/***********************************************************************************
	 * Setup our chapter menu items
	 ***********************************************************************************/
	(function(window, videojs) {
	 	var defaults = {
	 		list_chap: {},
			ui: true
	 	};
	 	
		/***********************************************************************************
		 * Setup our chapter menu items
		 ***********************************************************************************/
		var MenuItem = videojs.getComponent('MenuItem');
		var ChapterMenuItem = videojs.extend(MenuItem, {
		 	constructor: function(player, options) {
				// Modify options for parent MenuItem class's init.
				options.label = methods.chap_label(options.chap);
				//options.selected = (options.chap === player.getCurrentChap());

				// Call the parent constructor
				MenuItem.call(this, player, options);

				// Store the resolution as a call property
				this.chapter = options.chap;

				// Register our click handler
				this.on(['click', 'tap'], this.onClick);

				// Copy the player as a class property
				this.player = player;
			}
		});
		// Handle clicks on the menu items
		ChapterMenuItem.prototype.onClick = function() {
			this.player_.currentTime(this.chapter);
		};
		MenuItem.registerComponent('ChapterMenuItem', ChapterMenuItem);
		  
		/***********************************************************************************
		 * Setup our chapter menu title item
		 ***********************************************************************************/
		var ChapterTitleMenuItem = videojs.extend(MenuItem, {
		 	constructor: function(player, options) {
				// Call the parent constructor
				MenuItem.call(this, player, options);

				// No click handler for the menu title
				this.off('click');
			}
		});
		MenuItem.registerComponent('ChapterTitleMenuItem', ChapterTitleMenuItem);
		 
		/***********************************************************************************
		 * Define our chapter selector button
		 ***********************************************************************************/
		var MenuButton = videojs.getComponent('MenuButton');
		var ChapterSelectorButton = videojs.extend(MenuButton, {
		 	constructor: function(player, options) {
				// Copy the player as an accessible class property
				//this.player = player;
				// Add our list of available resolutions to the player object
				player.availablechap = options.available_chap;
				// Call the parent constructor
				MenuButton.call(this, player, options);
	    	}
		});
		 
		// Set class for resolution selector button
		ChapterSelectorButton.prototype.buildCSSClass = function() {
			return MenuButton.prototype.buildCSSClass.call(this) + ' vjs-chapters-button';
		}
		//ChapterSelectorButton.prototype.className = 'vjs-chapters-button';
		
		// Create a menu item for each available chapter
		ChapterSelectorButton.prototype.createItems = function() {
			var player = this.player_,
			items = [],
			current_chap;
			
			// Add the menu title item
			items.push(new ChapterTitleMenuItem(player, {
				el: videojs.dom.createEl('li', {
					className: 'vjs-menu-title vjs-chap-menu-title',
					innerHTML: 'Chapter'
				})
			}));

			// Add an item for each available chapter
			for (current_chap in player.availablechap) {
				if ('length' == current_chap) {
					continue;
				}
        
				items.push(new ChapterMenuItem(player, {
					chap : player.availablechap[current_chap]
				}));
			}

			return items;
		};
		MenuButton.registerComponent('ChapterSelectorButton', ChapterSelectorButton);
		
		/***********************************************************************************
		 * Register the plugin with videojs, main plugin function
		 ***********************************************************************************/
		videojsChapterSelector = function(options) {
			// Override default options with those provided
			var settings = videojs.mergeOptions(defaults, options),
			 player = this,
			 available_chap = { length: 0 },
			 chapterSelector;
			
			player.ready(function() {
				if (settings.list_chap != {}) {
					list_chap = settings.list_chap;
				}
				  
				for (var chap in list_chap) {
					available_chap.length++;
				  	available_chap[chap] = chap ;
				}
				  
				chapterSelector = new ChapterSelectorButton(player, {
				  	available_chap: available_chap
				});
				  
				// Add the button to the control bar object and the DOM
				player.controlBar.videojsChapterSelector = player.controlBar.addChild(chapterSelector);
				player.controlBar.videojsChapterSelector.dispose = function() {
					this.parentNode.removeChild(this);
				}
			});
		};

		// Register the plugin
		videojs.registerPlugin('videojsChapterSelector', videojsChapterSelector);	
	})(window, videojs);
})();
