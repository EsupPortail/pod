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
	var videojs = null;
	if(typeof window.videojs === 'undefined' && typeof require === 'function') {
		videojs = require('video.js');
	} else {
		videojs = window.videojs;
	}
	var list_disp = {};
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
		extend: function(destination, source) {
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
		 * @param	(string)	disp	The display to make a label for
		 *
		 * @returns	(string)	The label text string
		 */
		disp_label: function(disp) {
			return list_disp[disp];
		}
	};
	
	/***********************************************************************************
	 * Setup our display menu items
	 ***********************************************************************************/
	(function(window, videojs) {
		var defaults = {
			default_disp: '50/50',
			list_disp: {
		        '50/50': '50/50',
		        '30/70': '30/70',
		        '70/30': '70/30',
		        '100/20': 'Pip video',
		        '20/100': 'Pip media',
		        '100/0': 'only video',
		        '0/100': 'only media'
		    }
		};
	/***********************************************************************************
	 * Setup our display menu items
	 ***********************************************************************************/
		var MenuItem = videojs.getComponent('MenuItem');
		var DisplayMenuItem = videojs.extend(MenuItem, {
			constructor: function(player, options) {
				// Modify options for parent MenuItem class's init.
				options.label = methods.disp_label(options.disp);
				options.selected = (options.disp === player.getCurrentDisp());

				// Call the parent constructor
				MenuItem.call(this, player, options);

				// Store the display as a call property
				this.display = options.disp;

				// Register our click handler
				this.on('click', this.onClick);
				
				// Copy the player as a class property
				this.player = player;

				// Toggle the selected class whenever the display changes
				player.on('changeDisp', videojs.bind(this, function() {
					if (this.display == player.getCurrentDisp()) {
						this.selected(true);
					} else {
						this.selected(false);
					}
				}));
			}
		});

		// Handle clicks on the menu items
		DisplayMenuItem.prototype.onClick = function() {
			var player = this.player,
				button_nodes = player.controlBar.videojsDisplaySelector.el().firstChild.children,
				button_node_count = button_nodes.length;

			// Do nothing if we aren't changing displays
			if (player.getCurrentDisp() == this.display) {
	            return;
	        }

			// Save the newly selected display in our player options property
			player.currentDisp = this.display;

			// Update the button text
			while (button_node_count > 0) {
				button_node_count--;
				if ('vjs-icon-placeholder' == button_nodes[button_node_count].className) {
					button_nodes[button_node_count].innerHTML = methods.disp_label(this.display);
					break;
				}
			}

			// Update the classes to reflect the currently selected display
			player.trigger('changeDisp');
		};
		MenuItem.registerComponent('DisplayMenuItem', DisplayMenuItem);

		/***********************************************************************************
		 * Setup our display menu title item
		 ***********************************************************************************/
		var DisplayTitleMenuItem = videojs.extend(MenuItem, {
			constructor: function(player, options) {
				// Call the parent constructor
				MenuItem.call(this, player, options);

				// No click handler for the menu title
				this.off('click');
			}
		});
		MenuItem.registerComponent('DisplayTitleMenuItem', DisplayTitleMenuItem);

		/***********************************************************************************
		 * Define our display selector button
		 ***********************************************************************************/
		var MenuButton = videojs.getComponent('MenuButton');
		var DisplaySelectorButton = videojs.extend(MenuButton, {
			constructor: function(player, options) {
				// Add our list of available displays to the player object
				player.availableDisp = options.available_disp;
				// Call the parent constructor
				MenuButton.call(this, player, options);
				videojs.dom.addClass(this.el(), 'vjs-disp-button');
	            // Set the button text based on the option provided
	            this.el().firstChild.firstChild.innerHTML = options.buttonText;
			}
		});

		// Set class for resolution selector button
		DisplaySelectorButton.prototype.buildCSSClass = function() {
    		return MenuButton.prototype.buildCSSClass.call(this) + ' vjs-disp-button';
    	}

		// Create a menu item for each available display
		DisplaySelectorButton.prototype.createItems = function() {
			var player = this.player(),
				items = [],
				current_disp;

			// Add the menu title item
			items.push(new DisplayTitleMenuItem(player, {
				el: videojs.dom.createEl('li', {
					className: 'vjs-menu-title vjs-disp-menu-title',
					innerHTML: 'Display'
				})
			}));

			// Add an item for each available display
			for (current_disp in player.availableDisp) {
				if ('length' == current_disp) {
	                continue;
	            }

				items.push(new DisplayMenuItem(player, {
					disp: player.availableDisp[current_disp]
				}));
			}

			// Sort the available displays in descending order
			items.sort(function(a, b) {
				if (typeof a.display == 'undefined') {
					return -1;
				} else {
					return parseInt(b.display) - parseInt(a.display);
				}
			});

			return items;
		};
		MenuButton.registerComponent('DisplaySelectorButton', DisplaySelectorButton);

		/***********************************************************************************
		 * Register the plugin with videojs, main plugin function
		 ***********************************************************************************/
		videojsDisplaySelector = function(options) {
			// Override default options with those provided
			var settings = videojs.mergeOptions(defaults, options),
				player = this,
				available_disp = { length: 0 },
				current_disp,
				displaySelector;

			if (settings.list_disp != {}) {
	            list_disp = settings.list_disp;
	        }

			for (var disp in list_disp) {
	            available_disp.length++;
	            available_disp[disp] = disp;
	        }

			if (settings.default_disp) {
				player.currentDisp = settings.default_disp;
			}

			// Helper function to get the current display
			player.getCurrentDisp = function() {
				if (typeof player.currentDisp !== 'undefined') {
					return player.currentDisp;
				}
			};

			// Add the display selector button
			current_disp = player.getCurrentDisp();

			if (current_disp) {
	            current_disp = methods.disp_label(current_disp);
	        }

			displaySelector = new DisplaySelectorButton(player, {
	            buttonText: current_disp,
				available_disp: available_disp
			});

			// Add the button to the control bar object and the DOM
			player.controlBar.videojsDisplaySelector = player.controlBar.addChild(displaySelector);
		};
		videojs.registerPlugin('videojsDisplaySelector', videojsDisplaySelector);
	})(window, videojs);
})();