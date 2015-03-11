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

(function( _V_ ) {
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
	_V_.chapterMenuItem = _V_.MenuItem.extend({
        // Call variable to prevent the resolution change from being called twice
		/** @constructor */
		init : function(player, options) {
			// Modify options for parent MenuItem class's init.
			options.label = methods.chap_label(options.chap);
			//options.selected = (options.chap === player.getCurrentChap());

			// Call the parent constructor
			_V_.MenuItem.call(this, player, options);

			// Store the resolution as a call property
			this.chapter = options.chap;

			// Register our click handler
			this.on(['click', 'tap'], this.onClick);

			// Copy the player as a class property
			this.player = player;
		}
	});

	// Handle clicks on the menu items
	_V_.chapterMenuItem.prototype.onClick = function() {
		this.player.currentTime(this.chapter);
	};

	/***********************************************************************************
	 * Setup our chapter menu title item
	 ***********************************************************************************/
	_V_.chapterTitleMenuItem = _V_.MenuItem.extend({
        /** @constructor */
		init : function(player, options) {
			// Call the parent constructor
			_V_.MenuItem.call(this, player, options);

			// No click handler for the menu title
			this.off('click');
		}
	});

	/***********************************************************************************
	 * Define our chapter selector button
	 ***********************************************************************************/
	_V_.chapterSelector = _V_.MenuButton.extend({
		/** @constructor */
		init : function(player, options) {
			// Copy the player as an accessible class property
			//this.player = player;
			// Add our list of available resolutions to the player object
			player.availablechap = options.available_chap;
			// Call the parent constructor
			_V_.MenuButton.call(this, player, options);
            // Set the button text based on the option provided
            this.el().firstChild.firstChild.innerHTML = options.buttonText;
		}
	});

	// Set class for resolution selector button
    _V_.chapterSelector.prototype.className = 'vjs-chap-button';

	// Create a menu item for each available chapter
	_V_.chapterSelector.prototype.createItems = function() {
		var player = this.player(),
			items = [],
			current_chap;
		// Add the menu title item
		items.push(new _V_.chapterTitleMenuItem(player, {
			el: _V_.Component.prototype.createEl('li', {
				className: 'vjs-menu-title vjs-chap-menu-title',
				innerHTML: 'Chapter'
			})
		}));

		// Add an item for each available chapter
		for (current_chap in player.availablechap) {
			if ('length' == current_chap) {
                continue;
            }

			items.push(new _V_.chapterMenuItem(player, {
				chap : player.availablechap[current_chap]
			}));
		}

		return items;
	};

	/***********************************************************************************
	 * Register the plugin with videojs, main plugin function
	 ***********************************************************************************/
	_V_.plugin('chapterSelector', function(options) {
		// Only enable the plugin on HTML5 videos
		if (!this.el().firstChild.canPlayType) {
            return;
        }

		// Override default options with those provided
		var player = this,
			settings = methods.extend(
                {
				    list_chap: {}
			    },
                options || {}
            ),
			available_chap = { length: 0 },
			chapterSelector;
		
		if (settings.list_chap != {}) {
            list_chap = settings.list_chap;
        }
		
		for (var chap in list_chap) {
            available_chap.length++;
            available_chap[chap] = chap ;
        }
		
		chapterSelector = new _V_.chapterSelector(player, {
            buttonText: 'Chapter',
			available_chap: available_chap
		});
		
		// Add the button to the control bar object and the DOM
		player.controlBar.chapterSelector = player.controlBar.addChild(chapterSelector);
	});

})(videojs);
