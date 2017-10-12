(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// shim for using process in browser
var process = module.exports = {};

// cached from whatever global is present so that test runners that stub it
// don't break things.  But we need to wrap it in a try catch in case it is
// wrapped in strict mode code which doesn't define any globals.  It's inside a
// function because try/catches deoptimize in certain engines.

var cachedSetTimeout;
var cachedClearTimeout;

function defaultSetTimout() {
    throw new Error('setTimeout has not been defined');
}
function defaultClearTimeout () {
    throw new Error('clearTimeout has not been defined');
}
(function () {
    try {
        if (typeof setTimeout === 'function') {
            cachedSetTimeout = setTimeout;
        } else {
            cachedSetTimeout = defaultSetTimout;
        }
    } catch (e) {
        cachedSetTimeout = defaultSetTimout;
    }
    try {
        if (typeof clearTimeout === 'function') {
            cachedClearTimeout = clearTimeout;
        } else {
            cachedClearTimeout = defaultClearTimeout;
        }
    } catch (e) {
        cachedClearTimeout = defaultClearTimeout;
    }
} ())
function runTimeout(fun) {
    if (cachedSetTimeout === setTimeout) {
        //normal enviroments in sane situations
        return setTimeout(fun, 0);
    }
    // if setTimeout wasn't available but was latter defined
    if ((cachedSetTimeout === defaultSetTimout || !cachedSetTimeout) && setTimeout) {
        cachedSetTimeout = setTimeout;
        return setTimeout(fun, 0);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedSetTimeout(fun, 0);
    } catch(e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't trust the global object when called normally
            return cachedSetTimeout.call(null, fun, 0);
        } catch(e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error
            return cachedSetTimeout.call(this, fun, 0);
        }
    }


}
function runClearTimeout(marker) {
    if (cachedClearTimeout === clearTimeout) {
        //normal enviroments in sane situations
        return clearTimeout(marker);
    }
    // if clearTimeout wasn't available but was latter defined
    if ((cachedClearTimeout === defaultClearTimeout || !cachedClearTimeout) && clearTimeout) {
        cachedClearTimeout = clearTimeout;
        return clearTimeout(marker);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedClearTimeout(marker);
    } catch (e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't  trust the global object when called normally
            return cachedClearTimeout.call(null, marker);
        } catch (e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error.
            // Some versions of I.E. have different rules for clearTimeout vs setTimeout
            return cachedClearTimeout.call(this, marker);
        }
    }



}
var queue = [];
var draining = false;
var currentQueue;
var queueIndex = -1;

function cleanUpNextTick() {
    if (!draining || !currentQueue) {
        return;
    }
    draining = false;
    if (currentQueue.length) {
        queue = currentQueue.concat(queue);
    } else {
        queueIndex = -1;
    }
    if (queue.length) {
        drainQueue();
    }
}

function drainQueue() {
    if (draining) {
        return;
    }
    var timeout = runTimeout(cleanUpNextTick);
    draining = true;

    var len = queue.length;
    while(len) {
        currentQueue = queue;
        queue = [];
        while (++queueIndex < len) {
            if (currentQueue) {
                currentQueue[queueIndex].run();
            }
        }
        queueIndex = -1;
        len = queue.length;
    }
    currentQueue = null;
    draining = false;
    runClearTimeout(timeout);
}

process.nextTick = function (fun) {
    var args = new Array(arguments.length - 1);
    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args[i - 1] = arguments[i];
        }
    }
    queue.push(new Item(fun, args));
    if (queue.length === 1 && !draining) {
        runTimeout(drainQueue);
    }
};

// v8 likes predictible objects
function Item(fun, array) {
    this.fun = fun;
    this.array = array;
}
Item.prototype.run = function () {
    this.fun.apply(null, this.array);
};
process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];
process.version = ''; // empty string to avoid regexp issues
process.versions = {};

function noop() {}

process.on = noop;
process.addListener = noop;
process.once = noop;
process.off = noop;
process.removeListener = noop;
process.removeAllListeners = noop;
process.emit = noop;

process.binding = function (name) {
    throw new Error('process.binding is not supported');
};

process.cwd = function () { return '/' };
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};
process.umask = function() { return 0; };

},{}],2:[function(require,module,exports){
/*! npm.im/intervalometer */
'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

function intervalometer(cb, request, cancel, requestParameter) {
	var requestId;
	var previousLoopTime;
	function loop(now) {
		// must be requested before cb() because that might call .stop()
		requestId = request(loop, requestParameter);

		// called with "ms since last call". 0 on start()
		cb(now - (previousLoopTime || now));

		previousLoopTime = now;
	}
	return {
		start: function start() {
			if (!requestId) { // prevent double starts
				loop(0);
			}
		},
		stop: function stop() {
			cancel(requestId);
			requestId = null;
			previousLoopTime = 0;
		}
	};
}

function frameIntervalometer(cb) {
	return intervalometer(cb, requestAnimationFrame, cancelAnimationFrame);
}

function timerIntervalometer(cb, delay) {
	return intervalometer(cb, setTimeout, clearTimeout, delay);
}

exports.intervalometer = intervalometer;
exports.frameIntervalometer = frameIntervalometer;
exports.timerIntervalometer = timerIntervalometer;
},{}],3:[function(require,module,exports){
/*! npm.im/iphone-inline-video */
'use strict';

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

var Symbol = _interopDefault(require('poor-mans-symbol'));
var intervalometer = require('intervalometer');

function preventEvent(element, eventName, toggleProperty, preventWithProperty) {
	function handler(e) {
		if (Boolean(element[toggleProperty]) === Boolean(preventWithProperty)) {
			e.stopImmediatePropagation();
			// console.log(eventName, 'prevented on', element);
		}
		delete element[toggleProperty];
	}
	element.addEventListener(eventName, handler, false);

	// Return handler to allow to disable the prevention. Usage:
	// const preventionHandler = preventEvent(el, 'click');
	// el.removeEventHandler('click', preventionHandler);
	return handler;
}

function proxyProperty(object, propertyName, sourceObject, copyFirst) {
	function get() {
		return sourceObject[propertyName];
	}
	function set(value) {
		sourceObject[propertyName] = value;
	}

	if (copyFirst) {
		set(object[propertyName]);
	}

	Object.defineProperty(object, propertyName, {get: get, set: set});
}

function proxyEvent(object, eventName, sourceObject) {
	sourceObject.addEventListener(eventName, function () { return object.dispatchEvent(new Event(eventName)); });
}

function dispatchEventAsync(element, type) {
	Promise.resolve().then(function () {
		element.dispatchEvent(new Event(type));
	});
}

// iOS 10 adds support for native inline playback + silent autoplay
var isWhitelisted = /iPhone|iPod/i.test(navigator.userAgent) && !matchMedia('(-webkit-video-playable-inline)').matches;

var ಠ = Symbol();
var ಠevent = Symbol();
var ಠplay = Symbol('nativeplay');
var ಠpause = Symbol('nativepause');

/**
 * UTILS
 */

function getAudioFromVideo(video) {
	var audio = new Audio();
	proxyEvent(video, 'play', audio);
	proxyEvent(video, 'playing', audio);
	proxyEvent(video, 'pause', audio);
	audio.crossOrigin = video.crossOrigin;

	// 'data:' causes audio.networkState > 0
	// which then allows to keep <audio> in a resumable playing state
	// i.e. once you set a real src it will keep playing if it was if .play() was called
	audio.src = video.src || video.currentSrc || 'data:';

	// if (audio.src === 'data:') {
	//   TODO: wait for video to be selected
	// }
	return audio;
}

var lastRequests = [];
var requestIndex = 0;
var lastTimeupdateEvent;

function setTime(video, time, rememberOnly) {
	// allow one timeupdate event every 200+ ms
	if ((lastTimeupdateEvent || 0) + 200 < Date.now()) {
		video[ಠevent] = true;
		lastTimeupdateEvent = Date.now();
	}
	if (!rememberOnly) {
		video.currentTime = time;
	}
	lastRequests[++requestIndex % 3] = time * 100 | 0 / 100;
}

function isPlayerEnded(player) {
	return player.driver.currentTime >= player.video.duration;
}

function update(timeDiff) {
	var player = this;
	// console.log('update', player.video.readyState, player.video.networkState, player.driver.readyState, player.driver.networkState, player.driver.paused);
	if (player.video.readyState >= player.video.HAVE_FUTURE_DATA) {
		if (!player.hasAudio) {
			player.driver.currentTime = player.video.currentTime + ((timeDiff * player.video.playbackRate) / 1000);
			if (player.video.loop && isPlayerEnded(player)) {
				player.driver.currentTime = 0;
			}
		}
		setTime(player.video, player.driver.currentTime);
	} else if (player.video.networkState === player.video.NETWORK_IDLE && !player.video.buffered.length) {
		// this should happen when the source is available but:
		// - it's potentially playing (.paused === false)
		// - it's not ready to play
		// - it's not loading
		// If it hasAudio, that will be loaded in the 'emptied' handler below
		player.video.load();
		// console.log('Will load');
	}

	// console.assert(player.video.currentTime === player.driver.currentTime, 'Video not updating!');

	if (player.video.ended) {
		delete player.video[ಠevent]; // allow timeupdate event
		player.video.pause(true);
	}
}

/**
 * METHODS
 */

function play() {
	// console.log('play');
	var video = this;
	var player = video[ಠ];

	// if it's fullscreen, use the native player
	if (video.webkitDisplayingFullscreen) {
		video[ಠplay]();
		return;
	}

	if (player.driver.src !== 'data:' && player.driver.src !== video.src) {
		// console.log('src changed on play', video.src);
		setTime(video, 0, true);
		player.driver.src = video.src;
	}

	if (!video.paused) {
		return;
	}
	player.paused = false;

	if (!video.buffered.length) {
		// .load() causes the emptied event
		// the alternative is .play()+.pause() but that triggers play/pause events, even worse
		// possibly the alternative is preventing this event only once
		video.load();
	}

	player.driver.play();
	player.updater.start();

	if (!player.hasAudio) {
		dispatchEventAsync(video, 'play');
		if (player.video.readyState >= player.video.HAVE_ENOUGH_DATA) {
			// console.log('onplay');
			dispatchEventAsync(video, 'playing');
		}
	}
}
function pause(forceEvents) {
	// console.log('pause');
	var video = this;
	var player = video[ಠ];

	player.driver.pause();
	player.updater.stop();

	// if it's fullscreen, the developer the native player.pause()
	// This is at the end of pause() because it also
	// needs to make sure that the simulation is paused
	if (video.webkitDisplayingFullscreen) {
		video[ಠpause]();
	}

	if (player.paused && !forceEvents) {
		return;
	}

	player.paused = true;
	if (!player.hasAudio) {
		dispatchEventAsync(video, 'pause');
	}
	if (video.ended) {
		video[ಠevent] = true;
		dispatchEventAsync(video, 'ended');
	}
}

/**
 * SETUP
 */

function addPlayer(video, hasAudio) {
	var player = video[ಠ] = {};
	player.paused = true; // track whether 'pause' events have been fired
	player.hasAudio = hasAudio;
	player.video = video;
	player.updater = intervalometer.frameIntervalometer(update.bind(player));

	if (hasAudio) {
		player.driver = getAudioFromVideo(video);
	} else {
		video.addEventListener('canplay', function () {
			if (!video.paused) {
				// console.log('oncanplay');
				dispatchEventAsync(video, 'playing');
			}
		});
		player.driver = {
			src: video.src || video.currentSrc || 'data:',
			muted: true,
			paused: true,
			pause: function () {
				player.driver.paused = true;
			},
			play: function () {
				player.driver.paused = false;
				// media automatically goes to 0 if .play() is called when it's done
				if (isPlayerEnded(player)) {
					setTime(video, 0);
				}
			},
			get ended() {
				return isPlayerEnded(player);
			}
		};
	}

	// .load() causes the emptied event
	video.addEventListener('emptied', function () {
		// console.log('driver src is', player.driver.src);
		var wasEmpty = !player.driver.src || player.driver.src === 'data:';
		if (player.driver.src && player.driver.src !== video.src) {
			// console.log('src changed to', video.src);
			setTime(video, 0, true);
			player.driver.src = video.src;
			// playing videos will only keep playing if no src was present when .play()’ed
			if (wasEmpty) {
				player.driver.play();
			} else {
				player.updater.stop();
			}
		}
	}, false);

	// stop programmatic player when OS takes over
	video.addEventListener('webkitbeginfullscreen', function () {
		if (!video.paused) {
			// make sure that the <audio> and the syncer/updater are stopped
			video.pause();

			// play video natively
			video[ಠplay]();
		} else if (hasAudio && !player.driver.buffered.length) {
			// if the first play is native,
			// the <audio> needs to be buffered manually
			// so when the fullscreen ends, it can be set to the same current time
			player.driver.load();
		}
	});
	if (hasAudio) {
		video.addEventListener('webkitendfullscreen', function () {
			// sync audio to new video position
			player.driver.currentTime = video.currentTime;
			// console.assert(player.driver.currentTime === video.currentTime, 'Audio not synced');
		});

		// allow seeking
		video.addEventListener('seeking', function () {
			if (lastRequests.indexOf(video.currentTime * 100 | 0 / 100) < 0) {
				// console.log('User-requested seeking');
				player.driver.currentTime = video.currentTime;
			}
		});
	}
}

function overloadAPI(video) {
	var player = video[ಠ];
	video[ಠplay] = video.play;
	video[ಠpause] = video.pause;
	video.play = play;
	video.pause = pause;
	proxyProperty(video, 'paused', player.driver);
	proxyProperty(video, 'muted', player.driver, true);
	proxyProperty(video, 'playbackRate', player.driver, true);
	proxyProperty(video, 'ended', player.driver);
	proxyProperty(video, 'loop', player.driver, true);
	preventEvent(video, 'seeking');
	preventEvent(video, 'seeked');
	preventEvent(video, 'timeupdate', ಠevent, false);
	preventEvent(video, 'ended', ಠevent, false); // prevent occasional native ended events
}

function enableInlineVideo(video, hasAudio, onlyWhitelisted) {
	if ( hasAudio === void 0 ) hasAudio = true;
	if ( onlyWhitelisted === void 0 ) onlyWhitelisted = true;

	if ((onlyWhitelisted && !isWhitelisted) || video[ಠ]) {
		return;
	}
	addPlayer(video, hasAudio);
	overloadAPI(video);
	video.classList.add('IIV');
	if (!hasAudio && video.autoplay) {
		video.play();
	}
	if (!/iPhone|iPod|iPad/.test(navigator.platform)) {
		console.warn('iphone-inline-video is not guaranteed to work in emulated environments');
	}
}

enableInlineVideo.isWhitelisted = isWhitelisted;

module.exports = enableInlineVideo;
},{"intervalometer":2,"poor-mans-symbol":4}],4:[function(require,module,exports){
'use strict';

var index = typeof Symbol === 'undefined' ? function (description) {
	return '@' + (description || '@') + Math.random();
} : Symbol;

module.exports = index;
},{}],5:[function(require,module,exports){
/*!
 * EventEmitter v5.1.0 - git.io/ee
 * Unlicense - http://unlicense.org/
 * Oliver Caldwell - http://oli.me.uk/
 * @preserve
 */

;(function (exports) {
    'use strict';

    /**
     * Class for managing events.
     * Can be extended to provide event functionality in other classes.
     *
     * @class EventEmitter Manages event registering and emitting.
     */
    function EventEmitter() {}

    // Shortcuts to improve speed and size
    var proto = EventEmitter.prototype;
    var originalGlobalValue = exports.EventEmitter;

    /**
     * Finds the index of the listener for the event in its storage array.
     *
     * @param {Function[]} listeners Array of listeners to search through.
     * @param {Function} listener Method to look for.
     * @return {Number} Index of the specified listener, -1 if not found
     * @api private
     */
    function indexOfListener(listeners, listener) {
        var i = listeners.length;
        while (i--) {
            if (listeners[i].listener === listener) {
                return i;
            }
        }

        return -1;
    }

    /**
     * Alias a method while keeping the context correct, to allow for overwriting of target method.
     *
     * @param {String} name The name of the target method.
     * @return {Function} The aliased method
     * @api private
     */
    function alias(name) {
        return function aliasClosure() {
            return this[name].apply(this, arguments);
        };
    }

    /**
     * Returns the listener array for the specified event.
     * Will initialise the event object and listener arrays if required.
     * Will return an object if you use a regex search. The object contains keys for each matched event. So /ba[rz]/ might return an object containing bar and baz. But only if you have either defined them with defineEvent or added some listeners to them.
     * Each property in the object response is an array of listener functions.
     *
     * @param {String|RegExp} evt Name of the event to return the listeners from.
     * @return {Function[]|Object} All listener functions for the event.
     */
    proto.getListeners = function getListeners(evt) {
        var events = this._getEvents();
        var response;
        var key;

        // Return a concatenated array of all matching events if
        // the selector is a regular expression.
        if (evt instanceof RegExp) {
            response = {};
            for (key in events) {
                if (events.hasOwnProperty(key) && evt.test(key)) {
                    response[key] = events[key];
                }
            }
        }
        else {
            response = events[evt] || (events[evt] = []);
        }

        return response;
    };

    /**
     * Takes a list of listener objects and flattens it into a list of listener functions.
     *
     * @param {Object[]} listeners Raw listener objects.
     * @return {Function[]} Just the listener functions.
     */
    proto.flattenListeners = function flattenListeners(listeners) {
        var flatListeners = [];
        var i;

        for (i = 0; i < listeners.length; i += 1) {
            flatListeners.push(listeners[i].listener);
        }

        return flatListeners;
    };

    /**
     * Fetches the requested listeners via getListeners but will always return the results inside an object. This is mainly for internal use but others may find it useful.
     *
     * @param {String|RegExp} evt Name of the event to return the listeners from.
     * @return {Object} All listener functions for an event in an object.
     */
    proto.getListenersAsObject = function getListenersAsObject(evt) {
        var listeners = this.getListeners(evt);
        var response;

        if (listeners instanceof Array) {
            response = {};
            response[evt] = listeners;
        }

        return response || listeners;
    };

    function isValidListener (listener) {
        if (typeof listener === 'function' || listener instanceof RegExp) {
            return true
        } else if (listener && typeof listener === 'object') {
            return isValidListener(listener.listener)
        } else {
            return false
        }
    }

    /**
     * Adds a listener function to the specified event.
     * The listener will not be added if it is a duplicate.
     * If the listener returns true then it will be removed after it is called.
     * If you pass a regular expression as the event name then the listener will be added to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to attach the listener to.
     * @param {Function} listener Method to be called when the event is emitted. If the function returns true then it will be removed after calling.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addListener = function addListener(evt, listener) {
        if (!isValidListener(listener)) {
            throw new TypeError('listener must be a function');
        }

        var listeners = this.getListenersAsObject(evt);
        var listenerIsWrapped = typeof listener === 'object';
        var key;

        for (key in listeners) {
            if (listeners.hasOwnProperty(key) && indexOfListener(listeners[key], listener) === -1) {
                listeners[key].push(listenerIsWrapped ? listener : {
                    listener: listener,
                    once: false
                });
            }
        }

        return this;
    };

    /**
     * Alias of addListener
     */
    proto.on = alias('addListener');

    /**
     * Semi-alias of addListener. It will add a listener that will be
     * automatically removed after its first execution.
     *
     * @param {String|RegExp} evt Name of the event to attach the listener to.
     * @param {Function} listener Method to be called when the event is emitted. If the function returns true then it will be removed after calling.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addOnceListener = function addOnceListener(evt, listener) {
        return this.addListener(evt, {
            listener: listener,
            once: true
        });
    };

    /**
     * Alias of addOnceListener.
     */
    proto.once = alias('addOnceListener');

    /**
     * Defines an event name. This is required if you want to use a regex to add a listener to multiple events at once. If you don't do this then how do you expect it to know what event to add to? Should it just add to every possible match for a regex? No. That is scary and bad.
     * You need to tell it what event names should be matched by a regex.
     *
     * @param {String} evt Name of the event to create.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.defineEvent = function defineEvent(evt) {
        this.getListeners(evt);
        return this;
    };

    /**
     * Uses defineEvent to define multiple events.
     *
     * @param {String[]} evts An array of event names to define.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.defineEvents = function defineEvents(evts) {
        for (var i = 0; i < evts.length; i += 1) {
            this.defineEvent(evts[i]);
        }
        return this;
    };

    /**
     * Removes a listener function from the specified event.
     * When passed a regular expression as the event name, it will remove the listener from all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to remove the listener from.
     * @param {Function} listener Method to remove from the event.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeListener = function removeListener(evt, listener) {
        var listeners = this.getListenersAsObject(evt);
        var index;
        var key;

        for (key in listeners) {
            if (listeners.hasOwnProperty(key)) {
                index = indexOfListener(listeners[key], listener);

                if (index !== -1) {
                    listeners[key].splice(index, 1);
                }
            }
        }

        return this;
    };

    /**
     * Alias of removeListener
     */
    proto.off = alias('removeListener');

    /**
     * Adds listeners in bulk using the manipulateListeners method.
     * If you pass an object as the second argument you can add to multiple events at once. The object should contain key value pairs of events and listeners or listener arrays. You can also pass it an event name and an array of listeners to be added.
     * You can also pass it a regular expression to add the array of listeners to all events that match it.
     * Yeah, this function does quite a bit. That's probably a bad thing.
     *
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to add to multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to add.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addListeners = function addListeners(evt, listeners) {
        // Pass through to manipulateListeners
        return this.manipulateListeners(false, evt, listeners);
    };

    /**
     * Removes listeners in bulk using the manipulateListeners method.
     * If you pass an object as the second argument you can remove from multiple events at once. The object should contain key value pairs of events and listeners or listener arrays.
     * You can also pass it an event name and an array of listeners to be removed.
     * You can also pass it a regular expression to remove the listeners from all events that match it.
     *
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to remove from multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to remove.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeListeners = function removeListeners(evt, listeners) {
        // Pass through to manipulateListeners
        return this.manipulateListeners(true, evt, listeners);
    };

    /**
     * Edits listeners in bulk. The addListeners and removeListeners methods both use this to do their job. You should really use those instead, this is a little lower level.
     * The first argument will determine if the listeners are removed (true) or added (false).
     * If you pass an object as the second argument you can add/remove from multiple events at once. The object should contain key value pairs of events and listeners or listener arrays.
     * You can also pass it an event name and an array of listeners to be added/removed.
     * You can also pass it a regular expression to manipulate the listeners of all events that match it.
     *
     * @param {Boolean} remove True if you want to remove listeners, false if you want to add.
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to add/remove from multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to add/remove.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.manipulateListeners = function manipulateListeners(remove, evt, listeners) {
        var i;
        var value;
        var single = remove ? this.removeListener : this.addListener;
        var multiple = remove ? this.removeListeners : this.addListeners;

        // If evt is an object then pass each of its properties to this method
        if (typeof evt === 'object' && !(evt instanceof RegExp)) {
            for (i in evt) {
                if (evt.hasOwnProperty(i) && (value = evt[i])) {
                    // Pass the single listener straight through to the singular method
                    if (typeof value === 'function') {
                        single.call(this, i, value);
                    }
                    else {
                        // Otherwise pass back to the multiple function
                        multiple.call(this, i, value);
                    }
                }
            }
        }
        else {
            // So evt must be a string
            // And listeners must be an array of listeners
            // Loop over it and pass each one to the multiple method
            i = listeners.length;
            while (i--) {
                single.call(this, evt, listeners[i]);
            }
        }

        return this;
    };

    /**
     * Removes all listeners from a specified event.
     * If you do not specify an event then all listeners will be removed.
     * That means every event will be emptied.
     * You can also pass a regex to remove all events that match it.
     *
     * @param {String|RegExp} [evt] Optional name of the event to remove all listeners for. Will remove from every event if not passed.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeEvent = function removeEvent(evt) {
        var type = typeof evt;
        var events = this._getEvents();
        var key;

        // Remove different things depending on the state of evt
        if (type === 'string') {
            // Remove all listeners for the specified event
            delete events[evt];
        }
        else if (evt instanceof RegExp) {
            // Remove all events matching the regex.
            for (key in events) {
                if (events.hasOwnProperty(key) && evt.test(key)) {
                    delete events[key];
                }
            }
        }
        else {
            // Remove all listeners in all events
            delete this._events;
        }

        return this;
    };

    /**
     * Alias of removeEvent.
     *
     * Added to mirror the node API.
     */
    proto.removeAllListeners = alias('removeEvent');

    /**
     * Emits an event of your choice.
     * When emitted, every listener attached to that event will be executed.
     * If you pass the optional argument array then those arguments will be passed to every listener upon execution.
     * Because it uses `apply`, your array of arguments will be passed as if you wrote them out separately.
     * So they will not arrive within the array on the other side, they will be separate.
     * You can also pass a regular expression to emit to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to emit and execute listeners for.
     * @param {Array} [args] Optional array of arguments to be passed to each listener.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.emitEvent = function emitEvent(evt, args) {
        var listenersMap = this.getListenersAsObject(evt);
        var listeners;
        var listener;
        var i;
        var key;
        var response;

        for (key in listenersMap) {
            if (listenersMap.hasOwnProperty(key)) {
                listeners = listenersMap[key].slice(0);

                for (i = 0; i < listeners.length; i++) {
                    // If the listener returns true then it shall be removed from the event
                    // The function is executed either with a basic call or an apply if there is an args array
                    listener = listeners[i];

                    if (listener.once === true) {
                        this.removeListener(evt, listener.listener);
                    }

                    response = listener.listener.apply(this, args || []);

                    if (response === this._getOnceReturnValue()) {
                        this.removeListener(evt, listener.listener);
                    }
                }
            }
        }

        return this;
    };

    /**
     * Alias of emitEvent
     */
    proto.trigger = alias('emitEvent');

    /**
     * Subtly different from emitEvent in that it will pass its arguments on to the listeners, as opposed to taking a single array of arguments to pass on.
     * As with emitEvent, you can pass a regex in place of the event name to emit to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to emit and execute listeners for.
     * @param {...*} Optional additional arguments to be passed to each listener.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.emit = function emit(evt) {
        var args = Array.prototype.slice.call(arguments, 1);
        return this.emitEvent(evt, args);
    };

    /**
     * Sets the current value to check against when executing listeners. If a
     * listeners return value matches the one set here then it will be removed
     * after execution. This value defaults to true.
     *
     * @param {*} value The new value to check for when executing listeners.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.setOnceReturnValue = function setOnceReturnValue(value) {
        this._onceReturnValue = value;
        return this;
    };

    /**
     * Fetches the current value to check against when executing listeners. If
     * the listeners return value matches this one then it should be removed
     * automatically. It will return true by default.
     *
     * @return {*|Boolean} The current value to check for or the default, true.
     * @api private
     */
    proto._getOnceReturnValue = function _getOnceReturnValue() {
        if (this.hasOwnProperty('_onceReturnValue')) {
            return this._onceReturnValue;
        }
        else {
            return true;
        }
    };

    /**
     * Fetches the events object and creates one if required.
     *
     * @return {Object} The events storage object.
     * @api private
     */
    proto._getEvents = function _getEvents() {
        return this._events || (this._events = {});
    };

    /**
     * Reverts the global {@link EventEmitter} to its previous value and returns a reference to this version.
     *
     * @return {Function} Non conflicting EventEmitter class.
     */
    EventEmitter.noConflict = function noConflict() {
        exports.EventEmitter = originalGlobalValue;
        return EventEmitter;
    };

    // Expose the class either via AMD, CommonJS or the global object
    if (typeof define === 'function' && define.amd) {
        define(function () {
            return EventEmitter;
        });
    }
    else if (typeof module === 'object' && module.exports){
        module.exports = EventEmitter;
    }
    else {
        exports.EventEmitter = EventEmitter;
    }
}(this || {}));

},{}],6:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _BaseCanvas = require('./BaseCanvas');

var _BaseCanvas2 = _interopRequireDefault(_BaseCanvas);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Animation = function () {
    function Animation(player, options) {
        var _this = this;

        _classCallCheck(this, Animation);

        this._player = player;
        this._options = (0, _utils.mergeOptions)({}, this._options);
        this._options = (0, _utils.mergeOptions)(this._options, options);

        this._canvas = this._options.canvas;
        this._timeline = [];

        this._options.animation.forEach(function (obj) {
            _this.addTimeline(obj);
        });
    }

    _createClass(Animation, [{
        key: 'addTimeline',
        value: function addTimeline(opt) {
            var timeline = {
                active: false,
                initialized: false,
                completed: false,
                startValue: {},
                byValue: {},
                endValue: {},
                keyPoint: opt.keyPoint,
                duration: opt.duration,
                beginTime: Infinity,
                endTime: Infinity,
                onComplete: opt.onComplete,
                from: opt.from,
                to: opt.to
            };

            if (typeof opt.ease === "string") {
                timeline.ease = _utils.easeFunctions[opt.ease];
            }
            if (typeof opt.ease === "undefined") {
                timeline.ease = _utils.easeFunctions.linear;
            }

            this._timeline.push(timeline);
            this.attachEvents();
        }
    }, {
        key: 'initialTimeline',
        value: function initialTimeline(timeline) {
            for (var key in timeline.to) {
                if (timeline.to.hasOwnProperty(key)) {
                    var _from = timeline.from ? typeof timeline.from[key] !== "undefined" ? timeline.from[key] : this._canvas['_' + key] : this._canvas['_' + key];
                    timeline.startValue[key] = _from;
                    timeline.endValue[key] = timeline.to[key];
                    timeline.byValue[key] = timeline.to[key] - _from;
                }
            }
        }
    }, {
        key: 'processTimeline',
        value: function processTimeline(timeline, animationTime) {
            for (var key in timeline.to) {
                if (timeline.to.hasOwnProperty(key)) {
                    var newVal = timeline.ease && timeline.ease(animationTime, timeline.startValue[key], timeline.byValue[key], timeline.duration);
                    if (key === "fov") {
                        this._canvas._camera.fov = newVal;
                        this._canvas._camera.updateProjectionMatrix();
                    } else {
                        this._canvas['_' + key] = newVal;
                    }
                }
            }
        }
    }, {
        key: 'attachEvents',
        value: function attachEvents() {
            this._active = true;
            this._canvas.addListener("beforeRender", this.renderAnimation.bind(this));
            this._player.on("seeked", this.handleVideoSeek.bind(this));
        }
    }, {
        key: 'detachEvents',
        value: function detachEvents() {
            this._active = false;
            this._canvas.controlable = true;
            this._canvas.removeListener("beforeRender", this.renderAnimation.bind(this));
        }
    }, {
        key: 'handleVideoSeek',
        value: function handleVideoSeek() {
            var currentTime = this._player.getVideoEl().currentTime * 1000;
            var resetTimeline = 0;
            this._timeline.forEach(function (timeline) {
                var res = timeline.keyPoint >= currentTime || timeline.keyPoint <= currentTime && timeline.keyPoint + timeline.duration >= currentTime;
                if (res) {
                    resetTimeline++;
                    timeline.completed = false;
                    timeline.initialized = false;
                }
            });

            if (resetTimeline > 0 && !this._active) {
                this.attachEvents();
            }
        }
    }, {
        key: 'renderAnimation',
        value: function renderAnimation() {
            var _this2 = this;

            var currentTime = this._player.getVideoEl().currentTime * 1000;
            var completeTimeline = 0;
            var inActiveTimeline = 0;
            this._timeline.filter(function (timeline) {
                if (timeline.completed) {
                    completeTimeline++;
                    return false;
                }
                var res = timeline.keyPoint <= currentTime && timeline.keyPoint + timeline.duration > currentTime;
                timeline.active = res;
                if (timeline.active === false) inActiveTimeline++;

                if (res && !timeline.initialized) {
                    timeline.initialized = true;
                    timeline.beginTime = timeline.keyPoint;
                    timeline.endTime = timeline.beginTime + timeline.duration;
                    _this2.initialTimeline(timeline);
                }
                if (timeline.endTime <= currentTime) {
                    timeline.completed = true;
                    _this2.processTimeline(timeline, timeline.duration);
                    if (timeline.onComplete) {
                        timeline.onComplete.call(_this2);
                    }
                }
                return res;
            }).forEach(function (timeline) {
                var animationTime = currentTime - timeline.beginTime;
                _this2.processTimeline(timeline, animationTime);
            });

            this._canvas.controlable = inActiveTimeline === this._timeline.length;

            if (completeTimeline === this._timeline.length) {
                this.detachEvents();
            }
        }
    }]);

    return Animation;
}();

exports.default = Animation;

},{"../utils":36,"./BaseCanvas":7}],7:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

var _HelperCanvas = require('./HelperCanvas');

var _HelperCanvas2 = _interopRequireDefault(_HelperCanvas);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var HAVE_CURRENT_DATA = 2;

var BaseCanvas = function (_Component) {
    _inherits(BaseCanvas, _Component);

    /**
     * Base constructor
     * @param player
     * @param options
     */


    /**
     * Interaction
     */


    /**
     * Three.js
     */


    /**
     * Position
     */

    /**
     * Dimension
     */
    function BaseCanvas(player, options, renderElement) {
        _classCallCheck(this, BaseCanvas);

        var _this = _possibleConstructorReturn(this, (BaseCanvas.__proto__ || Object.getPrototypeOf(BaseCanvas)).call(this, player, options, renderElement));

        _this._width = _this.player.el().offsetWidth, _this._height = _this.player.el().offsetHeight;
        _this._lon = _this.options.initLon, _this._lat = _this.options.initLat, _this._phi = 0, _this._theta = 0;
        _this._accelector = {
            x: 0,
            y: 0
        };
        _this._renderer.setSize(_this._width, _this._height);

        //init interaction
        _this._mouseDown = false;
        _this._isUserInteracting = false;
        _this._runOnMobile = (0, _utils.mobileAndTabletcheck)();
        _this._VRMode = false;
        _this._controlable = true;

        _this._mouseDownPointer = {
            x: 0,
            y: 0
        };

        _this._mouseDownLocation = {
            Lat: 0,
            Lon: 0
        };

        _this.attachControlEvents();
        return _this;
    }

    _createClass(BaseCanvas, [{
        key: 'createEl',
        value: function createEl() {
            var tagName = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "div";
            var properties = arguments[1];
            var attributes = arguments[2];

            /**
             * initial webgl render
             */
            this._renderer = new _three2.default.WebGLRenderer();
            this._renderer.setPixelRatio(window.devicePixelRatio);
            this._renderer.autoClear = false;
            this._renderer.setClearColor(0x000000, 1);

            var renderElement = this._renderElement;

            if (renderElement.tagName.toLowerCase() === "video" && (this.options.useHelperCanvas === true || !(0, _utils.supportVideoTexture)(renderElement) && this.options.useHelperCanvas === "auto")) {
                this._helperCanvas = this.player.addComponent("HelperCanvas", new _HelperCanvas2.default(this.player));

                var context = this._helperCanvas.el();
                this._texture = new _three2.default.Texture(context);
            } else {
                this._texture = new _three2.default.Texture(renderElement);
            }

            this._texture.generateMipmaps = false;
            this._texture.minFilter = _three2.default.LinearFilter;
            this._texture.maxFilter = _three2.default.LinearFilter;
            this._texture.format = _three2.default.RGBFormat;

            var el = this._renderer.domElement;
            el.classList.add('vjs-panorama-canvas');

            return el;
        }
    }, {
        key: 'dispose',
        value: function dispose() {
            this.detachControlEvents();
            this.stopAnimation();
            _get(BaseCanvas.prototype.__proto__ || Object.getPrototypeOf(BaseCanvas.prototype), 'dispose', this).call(this);
        }
    }, {
        key: 'startAnimation',
        value: function startAnimation() {
            this._time = new Date().getTime();
            this.animate();
        }
    }, {
        key: 'stopAnimation',
        value: function stopAnimation() {
            if (this._requestAnimationId) {
                cancelAnimationFrame(this._requestAnimationId);
            }
        }
    }, {
        key: 'attachControlEvents',
        value: function attachControlEvents() {
            this.on('mousemove', this.handleMouseMove.bind(this));
            this.on('touchmove', this.handleTouchMove.bind(this));
            this.on('mousedown', this.handleMouseDown.bind(this));
            this.on('touchstart', this.handleTouchStart.bind(this));
            this.on('mouseup', this.handleMouseUp.bind(this));
            this.on('touchend', this.handleTouchEnd.bind(this));
            this.on('mouseenter', this.handleMouseEnter.bind(this));
            this.on('mouseleave', this.handleMouseLease.bind(this));
            if (this.options.scrollable) {
                this.on('mousewheel', this.handleMouseWheel.bind(this));
                this.on('MozMousePixelScroll', this.handleMouseWheel.bind(this));
            }
            if (this.options.resizable) {
                window.addEventListener("resize", this.handleResize.bind(this));
            }
            if (this.options.autoMobileOrientation) {
                window.addEventListener('devicemotion', this.handleMobileOrientation.bind(this));
            }
            if (this.options.KeyboardControl) {
                window.addEventListener('keydown', this.handleKeyDown.bind(this));
                window.addEventListener('keyup', this.handleKeyUp.bind(this));
            }
        }
    }, {
        key: 'detachControlEvents',
        value: function detachControlEvents() {
            this.off('mousemove', this.handleMouseMove.bind(this));
            this.off('touchmove', this.handleTouchMove.bind(this));
            this.off('mousedown', this.handleMouseDown.bind(this));
            this.off('touchstart', this.handleTouchStart.bind(this));
            this.off('mouseup', this.handleMouseUp.bind(this));
            this.off('touchend', this.handleTouchEnd.bind(this));
            this.off('mouseenter', this.handleMouseEnter.bind(this));
            this.off('mouseleave', this.handleMouseLease.bind(this));
            if (this.options.scrollable) {
                this.off('mousewheel', this.handleMouseWheel.bind(this));
                this.off('MozMousePixelScroll', this.handleMouseWheel.bind(this));
            }
            if (this.options.resizable) {
                window.removeEventListener("resize", this.handleResize.bind(this));
            }
            if (this.options.autoMobileOrientation) {
                window.removeEventListener('devicemotion', this.handleMobileOrientation.bind(this));
            }
            if (this.options.KeyboardControl) {
                window.removeEventListener('keydown', this.handleKeyDown.bind(this));
                window.removeEventListener('keyup', this.handleKeyUp.bind(this));
            }
        }

        /**
         * trigger when window resized
         */

    }, {
        key: 'handleResize',
        value: function handleResize() {
            this._width = this.player.el().offsetWidth, this._height = this.player.el().offsetHeight;
            this._renderer.setSize(this._width, this._height);
        }
    }, {
        key: 'handleMouseWheel',
        value: function handleMouseWheel(event) {
            event.stopPropagation();
            event.preventDefault();
        }
    }, {
        key: 'handleMouseEnter',
        value: function handleMouseEnter(event) {
            this._isUserInteracting = true;
            this._accelector.x = 0;
            this._accelector.y = 0;
        }
    }, {
        key: 'handleMouseLease',
        value: function handleMouseLease(event) {
            this._isUserInteracting = false;
            this._accelector.x = 0;
            this._accelector.y = 0;
            if (this._mouseDown) {
                this._mouseDown = false;
            }
        }
    }, {
        key: 'handleMouseDown',
        value: function handleMouseDown(event) {
            event.preventDefault();
            var clientX = event.clientX || event.touches && event.touches[0].clientX;
            var clientY = event.clientY || event.touches && event.touches[0].clientY;
            if (typeof clientX !== "undefined" && clientY !== "undefined") {
                this._mouseDown = true;
                this._mouseDownPointer.x = clientX;
                this._mouseDownPointer.y = clientY;
                this._mouseDownLocation.Lon = this._lon;
                this._mouseDownLocation.Lat = this._lat;
            }
        }
    }, {
        key: 'handleMouseMove',
        value: function handleMouseMove(event) {
            var clientX = event.clientX || event.touches && event.touches[0].clientX;
            var clientY = event.clientY || event.touches && event.touches[0].clientY;

            if (this.options.MouseEnable && this.controlable && typeof clientX !== "undefined" && typeof clientY !== "undefined") {
                if (this._mouseDown) {
                    this._lon = (this._mouseDownPointer.x - clientX) * 0.2 + this._mouseDownLocation.Lon;
                    this._lat = (clientY - this._mouseDownPointer.y) * 0.2 + this._mouseDownLocation.Lat;
                    this._accelector.x = 0;
                    this._accelector.y = 0;
                } else if (!this.options.clickAndDrag) {
                    var rect = this.el().getBoundingClientRect();
                    var x = clientX - this._width / 2 - rect.left;
                    var y = this._height / 2 - (clientY - rect.top);
                    var angle = 0;
                    if (x === 0) {
                        angle = y > 0 ? Math.PI / 2 : Math.PI * 3 / 2;
                    } else if (x > 0 && y > 0) {
                        angle = Math.atan(y / x);
                    } else if (x > 0 && y < 0) {
                        angle = 2 * Math.PI - Math.atan(y * -1 / x);
                    } else if (x < 0 && y > 0) {
                        angle = Math.PI - Math.atan(y / x * -1);
                    } else {
                        angle = Math.PI + Math.atan(y / x);
                    }
                    this._accelector.x = Math.cos(angle) * this.options.movingSpeed.x * Math.abs(x);
                    this._accelector.y = Math.sin(angle) * this.options.movingSpeed.y * Math.abs(y);
                }
            }
        }
    }, {
        key: 'handleMouseUp',
        value: function handleMouseUp(event) {
            this._mouseDown = false;
            if (this.options.clickToToggle) {
                var clientX = event.clientX || event.changedTouches && event.changedTouches[0].clientX;
                var clientY = event.clientY || event.changedTouches && event.changedTouches[0].clientY;
                if (typeof clientX !== "undefined" && clientY !== "undefined" && this.options.clickToToggle) {
                    var diffX = Math.abs(clientX - this._mouseDownPointer.x);
                    var diffY = Math.abs(clientY - this._mouseDownPointer.y);
                    if (diffX < 0.1 && diffY < 0.1) this.player.paused() ? this.player.play() : this.player.pause();
                }
            }
        }
    }, {
        key: 'handleTouchStart',
        value: function handleTouchStart(event) {
            if (event.touches.length > 1) {
                this._isUserPinch = true;
                this._multiTouchDistance = (0, _utils.getTouchesDistance)(event.touches);
            }
            this.handleMouseDown(event);
        }
    }, {
        key: 'handleTouchMove',
        value: function handleTouchMove(event) {
            this.trigger("touchMove");
            //handle single touch event,
            if (!this._isUserPinch || event.touches.length <= 1) {
                this.handleMouseMove(event);
            }
        }
    }, {
        key: 'handleTouchEnd',
        value: function handleTouchEnd(event) {
            this._isUserPinch = false;
            this.handleMouseUp(event);
        }
    }, {
        key: 'handleMobileOrientation',
        value: function handleMobileOrientation(event) {
            if (typeof event.rotationRate !== "undefined") {
                var x = event.rotationRate.alpha;
                var y = event.rotationRate.beta;
                var portrait = typeof event.portrait !== "undefined" ? event.portrait : window.matchMedia("(orientation: portrait)").matches;
                var landscape = typeof event.landscape !== "undefined" ? event.landscape : window.matchMedia("(orientation: landscape)").matches;
                var orientation = event.orientation || window.orientation;

                if (portrait) {
                    this._lon = this._lon - y * this.options.mobileVibrationValue;
                    this._lat = this._lat + x * this.options.mobileVibrationValue;
                } else if (landscape) {
                    var orientationDegree = -90;
                    if (typeof orientation !== "undefined") {
                        orientationDegree = orientation;
                    }

                    this._lon = orientationDegree === -90 ? this._lon + x * this.options.mobileVibrationValue : this._lon - x * this.options.mobileVibrationValue;
                    this._lat = orientationDegree === -90 ? this._lat + y * this.options.mobileVibrationValue : this._lat - y * this.options.mobileVibrationValue;
                }
            }
        }
    }, {
        key: 'handleKeyDown',
        value: function handleKeyDown(event) {
            this._isUserInteracting = true;
            switch (event.keyCode) {
                case 38: /*up*/
                case 87:
                    /*W*/
                    this._lat += this.options.KeyboardMovingSpeed.y;
                    break;
                case 37: /*left*/
                case 65:
                    /*A*/
                    this._lon -= this.options.KeyboardMovingSpeed.x;
                    break;
                case 39: /*right*/
                case 68:
                    /*D*/
                    this._lon += this.options.KeyboardMovingSpeed.x;
                    break;
                case 40: /*down*/
                case 83:
                    /*S*/
                    this._lat -= this.options.KeyboardMovingSpeed.y;
                    break;
            }
        }
    }, {
        key: 'handleKeyUp',
        value: function handleKeyUp(event) {
            this._isUserInteracting = false;
        }
    }, {
        key: 'enableVR',
        value: function enableVR() {
            this._VRMode = true;
        }
    }, {
        key: 'disableVR',
        value: function disableVR() {
            this._VRMode = false;
        }
    }, {
        key: 'animate',
        value: function animate() {
            this._requestAnimationId = requestAnimationFrame(this.animate.bind(this));
            var ct = new Date().getTime();
            if (ct - this._time >= 30) {
                this._texture.needsUpdate = true;
                this._time = ct;
                this.trigger("textureRender");
            }

            //canvas should only be rendered when video is ready or will report `no video` warning message.
            if (this._renderElement.tagName.toLowerCase() !== "video" || this.player.readyState() >= HAVE_CURRENT_DATA) {
                this.render();
            }
        }
    }, {
        key: 'render',
        value: function render() {
            this.trigger("beforeRender");
            if (this._controlable) {
                if (!this._isUserInteracting) {
                    var symbolLat = this._lat > this.options.initLat ? -1 : 1;
                    var symbolLon = this._lon > this.options.initLon ? -1 : 1;
                    if (this.options.backToInitLat) {
                        this._lat = this._lat > this.options.initLat - Math.abs(this.options.returnLatSpeed) && this._lat < this.options.initLat + Math.abs(this.options.returnLatSpeed) ? this.options.initLat : this._lat + this.options.returnLatSpeed * symbolLat;
                    }
                    if (this.options.backToInitLon) {
                        this._lon = this._lon > this.options.initLon - Math.abs(this.options.returnLonSpeed) && this._lon < this.options.initLon + Math.abs(this.options.returnLonSpeed) ? this.options.initLon : this._lon + this.options.returnLonSpeed * symbolLon;
                    }
                } else if (this._accelector.x !== 0 && this._accelector.y !== 0) {
                    this._lat += this._accelector.y;
                    this._lon += this._accelector.x;
                }
            }

            if (this._options.minLon === 0 && this._options.maxLon === 360) {
                if (this._lon > 360) {
                    this._lon -= 360;
                } else if (this._lon < 0) {
                    this._lon += 360;
                }
            }

            this._lat = Math.max(this.options.minLat, Math.min(this.options.maxLat, this._lat));
            this._lon = Math.max(this.options.minLon, Math.min(this.options.maxLon, this._lon));
            this._phi = _three2.default.Math.degToRad(90 - this._lat);
            this._theta = _three2.default.Math.degToRad(this._lon);

            if (this._helperCanvas) {
                this._helperCanvas.render();
            }
            this._renderer.clear();
            this.trigger("render");
        }
    }, {
        key: 'VRMode',
        get: function get() {
            return this._VRMode;
        }
    }, {
        key: 'controlable',
        get: function get() {
            return this._controlable;
        },
        set: function set(val) {
            this._controlable = val;
        }
    }]);

    return BaseCanvas;
}(_Component3.default);

exports.default = BaseCanvas;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"../utils":36,"./Component":10,"./HelperCanvas":14}],8:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _ClickableComponent2 = require('./ClickableComponent');

var _ClickableComponent3 = _interopRequireDefault(_ClickableComponent2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Button = function (_ClickableComponent) {
    _inherits(Button, _ClickableComponent);

    function Button(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        _classCallCheck(this, Button);

        var _this = _possibleConstructorReturn(this, (Button.__proto__ || Object.getPrototypeOf(Button)).call(this, player, options));

        _this.on("keydown", _this.handleKeyPress.bind(_this));
        return _this;
    }

    _createClass(Button, [{
        key: 'createEl',
        value: function createEl(tagName, properties, attributes) {
            return _get(Button.prototype.__proto__ || Object.getPrototypeOf(Button.prototype), 'createEl', this).call(this, "button", null, {
                type: "button",
                // let the screen reader user know that the text of the button may change
                'aria-live': 'polite'
            });
        }

        /**
         * Enable the `Button` element so that it can be activated or clicked. Use this with
         * {@link Button#disable}.
         */

    }, {
        key: 'enable',
        value: function enable() {
            this.el().removeAttribute('disabled');
        }

        /**
         * Enable the `Button` element so that it cannot be activated or clicked. Use this with
         * {@link Button#enable}.
         */

    }, {
        key: 'disable',
        value: function disable() {
            this.el().setAttribute('disabled', 'disabled');
        }
    }, {
        key: 'handleKeyPress',
        value: function handleKeyPress(event) {
            // Ignore Space (32) or Enter (13) key operation, which is handled by the browser for a button.
            if (event.which === 32 || event.which === 13) {
                return;
            }
        }
    }]);

    return Button;
}(_ClickableComponent3.default);

exports.default = Button;

},{"./ClickableComponent":9}],9:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ClickableComponent = function (_Component) {
    _inherits(ClickableComponent, _Component);

    function ClickableComponent(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        _classCallCheck(this, ClickableComponent);

        var _this = _possibleConstructorReturn(this, (ClickableComponent.__proto__ || Object.getPrototypeOf(ClickableComponent)).call(this, player, options));

        _this.on("click", _this.handleClick.bind(_this));
        _this.addListener("tap", _this.handleClick.bind(_this));
        return _this;
    }

    /**
     * Builds the default DOM `className`.
     *
     * @return {string}
     *         The DOM `className` for this object.
     */


    _createClass(ClickableComponent, [{
        key: 'buildCSSClass',
        value: function buildCSSClass() {
            return 'vjs-control vjs-button ' + _get(ClickableComponent.prototype.__proto__ || Object.getPrototypeOf(ClickableComponent.prototype), 'buildCSSClass', this).call(this);
        }
    }, {
        key: 'handleClick',
        value: function handleClick(event) {
            this.trigger("click");
        }
    }]);

    return ClickableComponent;
}(_Component3.default);

exports.default = ClickableComponent;

},{"./Component":10}],10:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _wolfy87Eventemitter = require('wolfy87-eventemitter');

var _wolfy87Eventemitter2 = _interopRequireDefault(_wolfy87Eventemitter);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } // @ flow

/**
 * base Component layer, which will be use when videojs is not supported environment.
 */
var Component = function (_EventEmitter) {
    _inherits(Component, _EventEmitter);

    function Component(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
        var renderElement = arguments[2];
        var ready = arguments[3];

        _classCallCheck(this, Component);

        var _this = _possibleConstructorReturn(this, (Component.__proto__ || Object.getPrototypeOf(Component)).call(this));

        _this._player = player;
        // Make a copy of prototype.options_ to protect against overriding defaults
        _this._options = (0, _utils.mergeOptions)({}, _this._options);
        // Updated options with supplied options
        _this._options = (0, _utils.mergeOptions)(_this._options, options);

        _this._renderElement = renderElement;

        // Get ID from options or options element if one is supplied
        _this._id = options.id || options.el && options.el.id;

        _this._el = options.el ? options.el : _this.createEl();

        _this.emitTapEvents();

        _this._children = [];

        if (ready) {
            ready.call(_this);
        }
        return _this;
    }

    _createClass(Component, [{
        key: 'dispose',
        value: function dispose() {
            for (var i = 0; i < this._children.length; i++) {
                this._children[i].component.dispose();
            }

            if (this._el) {
                if (this._el.parentNode) {
                    this._el.parentNode.removeChild(this._el);
                }

                this._el = null;
            }
        }

        /**
         * Emit a 'tap' events when touch event support gets detected. This gets used to
         * support toggling the controls through a tap on the video. They get enabled
         * because every sub-component would have extra overhead otherwise.
         * */

    }, {
        key: 'emitTapEvents',
        value: function emitTapEvents() {
            var _this2 = this;

            // Track the start time so we can determine how long the touch lasted
            var touchStart = 0;
            var firstTouch = null;

            // Maximum movement allowed during a touch event to still be considered a tap
            // Other popular libs use anywhere from 2 (hammer.js) to 15,
            // so 10 seems like a nice, round number.
            var tapMovementThreshold = 10;

            // The maximum length a touch can be while still being considered a tap
            var touchTimeThreshold = 200;

            var couldBeTap = void 0;

            this.on('touchstart', function (event) {
                // If more than one finger, don't consider treating this as a click
                if (event.touches.length === 1) {
                    // Copy pageX/pageY from the object
                    firstTouch = {
                        pageX: event.touches[0].pageX,
                        pageY: event.touches[0].pageY
                    };
                    // Record start time so we can detect a tap vs. "touch and hold"
                    touchStart = new Date().getTime();
                    // Reset couldBeTap tracking
                    couldBeTap = true;
                }
            });

            this.on('touchmove', function (event) {
                // If more than one finger, don't consider treating this as a click
                if (event.touches.length > 1) {
                    couldBeTap = false;
                } else if (firstTouch) {
                    // Some devices will throw touchmoves for all but the slightest of taps.
                    // So, if we moved only a small distance, this could still be a tap
                    var xdiff = event.touches[0].pageX - firstTouch.pageX;
                    var ydiff = event.touches[0].pageY - firstTouch.pageY;
                    var touchDistance = Math.sqrt(xdiff * xdiff + ydiff * ydiff);

                    if (touchDistance > tapMovementThreshold) {
                        couldBeTap = false;
                    }
                }
            });

            var noTap = function noTap() {
                couldBeTap = false;
            };

            // TODO: Listen to the original target. http://youtu.be/DujfpXOKUp8?t=13m8s
            this.on('touchleave', noTap);
            this.on('touchcancel', noTap);

            // When the touch ends, measure how long it took and trigger the appropriate
            // event
            this.on('touchend', function (event) {
                firstTouch = null;
                // Proceed only if the touchmove/leave/cancel event didn't happen
                if (couldBeTap === true) {
                    // Measure how long the touch lasted
                    var touchTime = new Date().getTime() - touchStart;

                    // Make sure the touch was less than the threshold to be considered a tap
                    if (touchTime < touchTimeThreshold) {
                        // Don't let browser turn this into a click
                        event.preventDefault();
                        /**
                         * Triggered when a `Component` is tapped.
                         *
                         * @event Component#tap
                         * @type {EventTarget~Event}
                         */
                        _this2.trigger('tap');
                        // It may be good to copy the touchend event object and change the
                        // type to tap, if the other event properties aren't exact after
                        // Events.fixEvent runs (e.g. event.target)
                    }
                }
            });
        }
    }, {
        key: 'createEl',
        value: function createEl() {
            var tagName = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "div";
            var properties = arguments[1];
            var attributes = arguments[2];

            var el = document.createElement(tagName);
            el.className = this.buildCSSClass();

            for (var attribute in attributes) {
                if (attributes.hasOwnProperty(attribute)) {
                    var value = attributes[attribute];
                    el.setAttribute(attribute, value);
                }
            }
            return el;
        }
    }, {
        key: 'el',
        value: function el() {
            return this._el;
        }

        /**
         * Builds the default DOM class name. Should be overriden by sub-components.
         *
         * @return {string}
         *         The DOM class name for this object.
         *
         * @abstract
         */

    }, {
        key: 'buildCSSClass',
        value: function buildCSSClass() {
            // Child classes can include a function that does:
            // return 'CLASS NAME' + this._super();
            return '';
        }
    }, {
        key: 'on',
        value: function on(name, action) {
            this.el().addEventListener(name, action);
        }
    }, {
        key: 'off',
        value: function off(name, action) {
            this.el().removeEventListener(name, action);
        }
    }, {
        key: 'one',
        value: function one(name, action) {
            var _this3 = this;

            var _oneTimeFunction = void 0;
            this.on(name, _oneTimeFunction = function oneTimeFunction() {
                action();
                _this3.off(name, _oneTimeFunction);
            });
        }

        //Do nothing by default

    }, {
        key: 'handleResize',
        value: function handleResize() {}
    }, {
        key: 'addClass',
        value: function addClass(name) {
            this.el().classList.add(name);
        }
    }, {
        key: 'removeClass',
        value: function removeClass(name) {
            this.el().classList.remove(name);
        }
    }, {
        key: 'toggleClass',
        value: function toggleClass(name) {
            this.el().classList.toggle(name);
        }
    }, {
        key: 'show',
        value: function show() {
            this.el().style.display = "block";
        }
    }, {
        key: 'hide',
        value: function hide() {
            this.el().style.display = "none";
        }
    }, {
        key: 'addChild',
        value: function addChild(name, component, index) {
            var location = this.el();
            if (!index) {
                index = -1;
            }

            if (typeof component.el === "function" && component.el()) {
                if (index === -1) {
                    location.appendChild(component.el());
                } else {
                    var children = location.childNodes;
                    var child = children[index];
                    location.insertBefore(component.el(), child);
                }
            }

            this._children.push({
                name: name,
                component: component,
                location: location
            });
        }
    }, {
        key: 'removeChild',
        value: function removeChild(name) {
            this._children = this._children.reduce(function (acc, component) {
                if (component.name !== name) {
                    acc.push(component);
                } else {
                    component.component.dispose();
                }
                return acc;
            }, []);
        }
    }, {
        key: 'getChild',
        value: function getChild(name) {
            var component = void 0;
            for (var i = 0; i < this._children.length; i++) {
                if (this._children[i].name === name) {
                    component = this._children[i];
                    break;
                }
            }
            return component ? component.component : null;
        }
    }, {
        key: 'player',
        get: function get() {
            return this._player;
        }
    }, {
        key: 'options',
        get: function get() {
            return this._options;
        }
    }]);

    return Component;
}(_wolfy87Eventemitter2.default);

exports.default = Component;

},{"../utils":36,"wolfy87-eventemitter":5}],11:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _TwoDVideo2 = require('./TwoDVideo');

var _TwoDVideo3 = _interopRequireDefault(_TwoDVideo2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var DualFisheye = function (_TwoDVideo) {
    _inherits(DualFisheye, _TwoDVideo);

    function DualFisheye(player, options, renderElement) {
        _classCallCheck(this, DualFisheye);

        var _this = _possibleConstructorReturn(this, (DualFisheye.__proto__ || Object.getPrototypeOf(DualFisheye)).call(this, player, options, renderElement));

        var geometry = new _three2.default.SphereBufferGeometry(500, 60, 40).toNonIndexed();
        var normals = geometry.attributes.normal.array;
        var uvs = geometry.attributes.uv.array;
        var l = normals.length / 3;
        for (var i = 0; i < l / 2; i++) {
            var x = normals[i * 3 + 0];
            var y = normals[i * 3 + 1];
            var z = normals[i * 3 + 2];

            var r = x == 0 && z == 0 ? 1 : Math.acos(y) / Math.sqrt(x * x + z * z) * (2 / Math.PI);
            uvs[i * 2 + 0] = x * _this.options.dualFish.circle1.rx * r * _this.options.dualFish.circle1.coverX + _this.options.dualFish.circle1.x;
            uvs[i * 2 + 1] = z * _this.options.dualFish.circle1.ry * r * _this.options.dualFish.circle1.coverY + _this.options.dualFish.circle1.y;
        }
        for (var _i = l / 2; _i < l; _i++) {
            var _x = normals[_i * 3 + 0];
            var _y = normals[_i * 3 + 1];
            var _z = normals[_i * 3 + 2];

            var _r = _x == 0 && _z == 0 ? 1 : Math.acos(-_y) / Math.sqrt(_x * _x + _z * _z) * (2 / Math.PI);
            uvs[_i * 2 + 0] = -_x * _this.options.dualFish.circle2.rx * _r * _this.options.dualFish.circle2.coverX + _this.options.dualFish.circle2.x;
            uvs[_i * 2 + 1] = _z * _this.options.dualFish.circle2.ry * _r * _this.options.dualFish.circle2.coverY + _this.options.dualFish.circle2.y;
        }
        geometry.rotateX(_this.options.Sphere.rotateX);
        geometry.rotateY(_this.options.Sphere.rotateY);
        geometry.rotateZ(_this.options.Sphere.rotateZ);
        geometry.scale(-1, 1, 1);

        //define mesh
        _this._mesh = new _three2.default.Mesh(geometry, new _three2.default.MeshBasicMaterial({ map: _this._texture }));
        _this._scene.add(_this._mesh);
        return _this;
    }

    return DualFisheye;
}(_TwoDVideo3.default);

exports.default = DualFisheye;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./TwoDVideo":21}],12:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _TwoDVideo2 = require('./TwoDVideo');

var _TwoDVideo3 = _interopRequireDefault(_TwoDVideo2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Equirectangular = function (_TwoDVideo) {
    _inherits(Equirectangular, _TwoDVideo);

    function Equirectangular(player, options, renderElement) {
        _classCallCheck(this, Equirectangular);

        var _this = _possibleConstructorReturn(this, (Equirectangular.__proto__ || Object.getPrototypeOf(Equirectangular)).call(this, player, options, renderElement));

        var geometry = new _three2.default.SphereGeometry(500, 60, 40);
        geometry.scale(-1, 1, 1);
        //define mesh
        _this._mesh = new _three2.default.Mesh(geometry, new _three2.default.MeshBasicMaterial({ map: _this._texture }));
        _this._scene.add(_this._mesh);
        return _this;
    }

    return Equirectangular;
}(_TwoDVideo3.default);

exports.default = Equirectangular;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./TwoDVideo":21}],13:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _TwoDVideo2 = require('./TwoDVideo');

var _TwoDVideo3 = _interopRequireDefault(_TwoDVideo2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Fisheye = function (_TwoDVideo) {
    _inherits(Fisheye, _TwoDVideo);

    function Fisheye(player, options, renderElement) {
        _classCallCheck(this, Fisheye);

        var _this = _possibleConstructorReturn(this, (Fisheye.__proto__ || Object.getPrototypeOf(Fisheye)).call(this, player, options, renderElement));

        var geometry = new _three2.default.SphereBufferGeometry(500, 60, 40).toNonIndexed();
        var normals = geometry.attributes.normal.array;
        var uvs = geometry.attributes.uv.array;
        for (var i = 0, l = normals.length / 3; i < l; i++) {
            var x = normals[i * 3 + 0];
            var y = normals[i * 3 + 1];
            var z = normals[i * 3 + 2];

            var r = Math.asin(Math.sqrt(x * x + z * z) / Math.sqrt(x * x + y * y + z * z)) / Math.PI;
            if (y < 0) r = 1 - r;
            var theta = x === 0 && z === 0 ? 0 : Math.acos(x / Math.sqrt(x * x + z * z));
            if (z < 0) theta = theta * -1;
            uvs[i * 2 + 0] = -0.8 * r * Math.cos(theta) + 0.5;
            uvs[i * 2 + 1] = 0.8 * r * Math.sin(theta) + 0.5;
        }
        geometry.rotateX(_this.options.Sphere.rotateX);
        geometry.rotateY(_this.options.Sphere.rotateY);
        geometry.rotateZ(_this.options.Sphere.rotateZ);
        geometry.scale(-1, 1, 1);
        //define mesh
        _this._mesh = new _three2.default.Mesh(geometry, new _three2.default.MeshBasicMaterial({ map: _this._texture }));
        _this._scene.add(_this._mesh);
        return _this;
    }

    return Fisheye;
}(_TwoDVideo3.default);

exports.default = Fisheye;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./TwoDVideo":21}],14:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var HelperCanvas = function (_Component) {
    _inherits(HelperCanvas, _Component);

    function HelperCanvas(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        _classCallCheck(this, HelperCanvas);

        var element = document.createElement('canvas');
        element.className = "vjs-panorama-video-helper-canvas";
        options.el = element;

        var _this = _possibleConstructorReturn(this, (HelperCanvas.__proto__ || Object.getPrototypeOf(HelperCanvas)).call(this, player, options));

        _this._videoElement = player.getVideoEl();
        _this._width = _this._videoElement.offsetWidth;
        _this._height = _this._videoElement.offsetHeight;

        _this.updateDimention();
        element.style.display = "none";

        _this._context = element.getContext('2d');
        _this._context.drawImage(_this._videoElement, 0, 0, _this._width, _this._height);
        /**
         * Get actual video dimension after video load.
         */
        player.one("loadedmetadata", function () {
            _this._width = _this._videoElement.videoWidth;
            _this._height = _this._videoElement.videoHeight;
            _this.updateDimention();
            _this.render();
        });
        return _this;
    }

    _createClass(HelperCanvas, [{
        key: 'updateDimention',
        value: function updateDimention() {
            this.el().width = this._width;
            this.el().height = this._height;
        }
    }, {
        key: 'el',
        value: function el() {
            return this._el;
        }
    }, {
        key: 'render',
        value: function render() {
            this._context.drawImage(this._videoElement, 0, 0, this._width, this._height);
        }
    }]);

    return HelperCanvas;
}(_Component3.default);

exports.default = HelperCanvas;

},{"./Component":10}],15:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

var _BaseCanvas = require('./BaseCanvas');

var _BaseCanvas2 = _interopRequireDefault(_BaseCanvas);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var defaults = {
    keyPoint: -1,
    duration: -1
};

var Marker = function (_Component) {
    _inherits(Marker, _Component);

    function Marker(player, options) {
        _classCallCheck(this, Marker);

        var el = void 0;

        var elem = options.element;
        if (typeof elem === "string") {
            el = document.createElement('div');
            el.innerText = elem;
        } else {
            el = elem;
        }
        el.id = options.id || "";
        el.className = "vjs-marker";

        options.el = el;

        var _this = _possibleConstructorReturn(this, (Marker.__proto__ || Object.getPrototypeOf(Marker)).call(this, player, options));

        _this._options = (0, _utils.mergeOptions)({}, defaults, options);

        var phi = _three2.default.Math.degToRad(90 - options.location.lat);
        var theta = _three2.default.Math.degToRad(options.location.lon);
        _this._position = new _three2.default.Vector3(options.radius * Math.sin(phi) * Math.cos(theta), options.radius * Math.cos(phi), options.radius * Math.sin(phi) * Math.sin(theta));
        if (_this.options.keyPoint < 0) {
            _this.enableMarker();
        }
        return _this;
    }

    _createClass(Marker, [{
        key: 'enableMarker',
        value: function enableMarker() {
            this._enable = true;
            this.addClass("vjs-marker--enable");
            if (this.options.onShow) {
                this.options.onShow.call(null);
            }
        }
    }, {
        key: 'disableMarker',
        value: function disableMarker() {
            this._enable = false;
            this.removeClass("vjs-marker--enable");
            if (this.options.onHide) {
                this.options.onHide.call(null);
            }
        }
    }, {
        key: 'render',
        value: function render(canvas, camera) {
            var angle = this._position.angleTo(camera.target);
            if (angle > Math.PI * 0.4) {
                this.addClass("vjs-marker--backside");
            } else {
                this.removeClass("vjs-marker--backside");
                var vector = this._position.clone().project(camera);
                var width = canvas.VRMode ? canvas._width / 2 : canvas._width;
                var point = {
                    x: (vector.x + 1) / 2 * width,
                    y: -(vector.y - 1) / 2 * canvas._height
                };
                this.el().style.transform = 'translate(' + point.x + 'px, ' + point.y + 'px)';
            }
        }
    }, {
        key: 'enable',
        get: function get() {
            return this._enable;
        }
    }, {
        key: 'position',
        get: function get() {
            return this._position;
        }
    }]);

    return Marker;
}(_Component3.default);

exports.default = Marker;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"../utils":36,"./BaseCanvas":7,"./Component":10}],16:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _BaseCanvas = require('./BaseCanvas');

var _BaseCanvas2 = _interopRequireDefault(_BaseCanvas);

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

var _MarkerGroup = require('./MarkerGroup');

var _MarkerGroup2 = _interopRequireDefault(_MarkerGroup);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var MarkerContainer = function (_Component) {
    _inherits(MarkerContainer, _Component);

    function MarkerContainer(player, options) {
        _classCallCheck(this, MarkerContainer);

        var _this = _possibleConstructorReturn(this, (MarkerContainer.__proto__ || Object.getPrototypeOf(MarkerContainer)).call(this, player, options));

        _this.el().classList.add("vjs-marker-container");
        _this._canvas = _this.options.canvas;

        if (_this.options.VREnable) {
            (function () {
                var leftMarkerGroup = new _MarkerGroup2.default(_this.player, {
                    id: "left_group",
                    canvas: _this._canvas,
                    markers: _this.options.markers,
                    camera: _this._canvas._camera
                });

                var markersSettings = _this.options.markers.map(function (marker) {
                    var newMarker = (0, _utils.mergeOptions)({}, marker);
                    newMarker.onShow = undefined;
                    newMarker.onHide = undefined;
                    return newMarker;
                });
                var rightMarkerGroup = new _MarkerGroup2.default(_this.player, {
                    id: "right_group",
                    canvas: _this._canvas,
                    markers: markersSettings,
                    camera: _this._canvas._camera
                });
                _this.addChild("leftMarkerGroup", leftMarkerGroup);
                _this.addChild("rightMarkerGroup", rightMarkerGroup);

                leftMarkerGroup.attachEvents();
                if (_this._canvas.VRMode) {
                    rightMarkerGroup.attachEvents();
                }

                _this.player.on("VRModeOn", function () {
                    _this.el().classList.add("vjs-marker-container--VREnable");
                    leftMarkerGroup.camera = _this._canvas._cameraL;
                    rightMarkerGroup.camera = _this._canvas._cameraR;
                    rightMarkerGroup.attachEvents();
                });

                _this.player.on("VRModeOff", function () {
                    _this.el().classList.remove("vjs-marker-container--VREnable");
                    leftMarkerGroup.camera = _this._canvas._camera;
                    rightMarkerGroup.detachEvents();
                });
            })();
        } else {
            var markerGroup = new _MarkerGroup2.default(_this.player, {
                id: "group",
                canvas: _this._canvas,
                markers: _this.options.markers,
                camera: _this._canvas._camera
            });
            _this.addChild("markerGroup", markerGroup);
            markerGroup.attachEvents();
        }
        return _this;
    }

    return MarkerContainer;
}(_Component3.default);

exports.default = MarkerContainer;

},{"../utils":36,"./BaseCanvas":7,"./Component":10,"./MarkerGroup":17}],17:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

var _BaseCanvas = require('./BaseCanvas');

var _BaseCanvas2 = _interopRequireDefault(_BaseCanvas);

var _Marker = require('./Marker');

var _Marker2 = _interopRequireDefault(_Marker);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var MarkerGroup = function (_Component) {
    _inherits(MarkerGroup, _Component);

    //save total markers enable to generate marker id
    function MarkerGroup(player, options) {
        _classCallCheck(this, MarkerGroup);

        var _this = _possibleConstructorReturn(this, (MarkerGroup.__proto__ || Object.getPrototypeOf(MarkerGroup)).call(this, player, options));

        _this._totalMarkers = 0;
        _this._markers = [];
        _this._camera = options.camera;
        _this.el().classList.add("vjs-marker-group");
        _this._canvas = options.canvas;

        _this.options.markers.forEach(function (markSetting) {
            _this.addMarker(markSetting);
        });

        _this.renderMarkers();
        return _this;
    }

    _createClass(MarkerGroup, [{
        key: 'attachEvents',
        value: function attachEvents() {
            this.el().classList.add("vjs-marker-group--enable");
            this.player.on("timeupdate", this.updateMarkers.bind(this));
            this._canvas.addListener("render", this.renderMarkers.bind(this));
        }
    }, {
        key: 'detachEvents',
        value: function detachEvents() {
            this.el().classList.remove("vjs-marker-group--enable");
            this.player.off("timeupdate", this.updateMarkers.bind(this));
            this._canvas.removeListener("render", this.renderMarkers.bind(this));
        }
    }, {
        key: 'addMarker',
        value: function addMarker(markSetting) {
            this._totalMarkers++;
            markSetting.id = this.options.id + '_' + (markSetting.id ? markSetting.id : 'marker_' + this._totalMarkers);
            var marker = new _Marker2.default(this.player, markSetting);
            this.addChild(markSetting.id, marker);
            this._markers.push(marker);
            return marker;
        }
    }, {
        key: 'removeMarker',
        value: function removeMarker(markerId) {
            this.removeChild(markerId);
        }
    }, {
        key: 'updateMarkers',
        value: function updateMarkers() {
            var currentTime = this.player.getVideoEl().currentTime * 1000;
            this._markers.forEach(function (marker) {
                //only check keypoint greater and equal zero
                if (marker.options.keyPoint >= 0) {
                    if (marker.options.duration > 0) {
                        marker.options.keyPoint <= currentTime && currentTime < marker.options.keyPoint + marker.options.duration ? !marker.enable && marker.enableMarker() : marker.enable && marker.disableMarker();
                    } else {
                        marker.options.keyPoint <= currentTime ? !marker.enable && marker.enableMarker() : marker.enable && marker.disableMarker();
                    }
                }
            });
        }
    }, {
        key: 'renderMarkers',
        value: function renderMarkers() {
            var _this2 = this;

            this._markers.forEach(function (marker) {
                if (marker.enable) {
                    marker.render(_this2._canvas, _this2._camera);
                }
            });
        }
    }, {
        key: 'camera',
        set: function set(camera) {
            this._camera = camera;
        }
    }]);

    return MarkerGroup;
}(_Component3.default);

exports.default = MarkerGroup;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./BaseCanvas":7,"./Component":10,"./Marker":15}],18:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Notification = function (_Component) {
    _inherits(Notification, _Component);

    function Notification(player, options) {
        _classCallCheck(this, Notification);

        var el = void 0;

        var message = options.Message;
        if (typeof message === 'string') {
            el = document.createElement('div');
            el.className = "vjs-video-notice-label vjs-video-notice-show";
            el.innerText = message;
        } else {
            el = message;
            el.classList.add("vjs-video-notice-show");
        }

        options.el = el;

        return _possibleConstructorReturn(this, (Notification.__proto__ || Object.getPrototypeOf(Notification)).call(this, player, options));
    }

    return Notification;
}(_Component3.default);

exports.default = Notification;

},{"./Component":10}],19:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _BaseCanvas2 = require('./BaseCanvas');

var _BaseCanvas3 = _interopRequireDefault(_BaseCanvas2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ThreeDVideo = function (_BaseCanvas) {
    _inherits(ThreeDVideo, _BaseCanvas);

    function ThreeDVideo(player, options, renderElement) {
        _classCallCheck(this, ThreeDVideo);

        //only show left part by default
        var _this = _possibleConstructorReturn(this, (ThreeDVideo.__proto__ || Object.getPrototypeOf(ThreeDVideo)).call(this, player, options, renderElement));

        _this._scene = new _three2.default.Scene();

        var aspectRatio = _this._width / _this._height;
        //define camera
        _this._cameraL = new _three2.default.PerspectiveCamera(_this.options.initFov, aspectRatio, 1, 2000);
        _this._cameraL.target = new _three2.default.Vector3(0, 0, 0);

        _this._cameraR = new _three2.default.PerspectiveCamera(_this.options.initFov, aspectRatio / 2, 1, 2000);
        _this._cameraR.position.set(1000, 0, 0);
        _this._cameraR.target = new _three2.default.Vector3(1000, 0, 0);
        return _this;
    }

    _createClass(ThreeDVideo, [{
        key: 'handleResize',
        value: function handleResize() {
            _get(ThreeDVideo.prototype.__proto__ || Object.getPrototypeOf(ThreeDVideo.prototype), 'handleResize', this).call(this);

            var aspectRatio = this._width / this._height;
            if (!this.VRMode) {
                this._cameraL.aspect = aspectRatio;
                this._cameraL.updateProjectionMatrix();
            } else {
                aspectRatio /= 2;
                this._cameraL.aspect = aspectRatio;
                this._cameraR.aspect = aspectRatio;
                this._cameraL.updateProjectionMatrix();
                this._cameraR.updateProjectionMatrix();
            }
        }
    }, {
        key: 'handleMouseWheel',
        value: function handleMouseWheel(event) {
            _get(ThreeDVideo.prototype.__proto__ || Object.getPrototypeOf(ThreeDVideo.prototype), 'handleMouseWheel', this).call(this, event);

            // WebKit
            if (event.wheelDeltaY) {
                this._cameraL.fov -= event.wheelDeltaY * 0.05;
                // Opera / Explorer 9
            } else if (event.wheelDelta) {
                this._cameraL.fov -= event.wheelDelta * 0.05;
                // Firefox
            } else if (event.detail) {
                this._cameraL.fov += event.detail * 1.0;
            }
            this._cameraL.fov = Math.min(this.options.maxFov, this._cameraL.fov);
            this._cameraL.fov = Math.max(this.options.minFov, this._cameraL.fov);
            this._cameraL.updateProjectionMatrix();
            if (this.VRMode) {
                this._cameraR.fov = this._cameraL.fov;
                this._cameraR.updateProjectionMatrix();
            }
        }
    }, {
        key: 'enableVR',
        value: function enableVR() {
            _get(ThreeDVideo.prototype.__proto__ || Object.getPrototypeOf(ThreeDVideo.prototype), 'enableVR', this).call(this);
            this._scene.add(this._meshR);
            this.handleResize();
        }
    }, {
        key: 'disableVR',
        value: function disableVR() {
            _get(ThreeDVideo.prototype.__proto__ || Object.getPrototypeOf(ThreeDVideo.prototype), 'disableVR', this).call(this);
            this._scene.remove(this._meshR);
            this.handleResize();
        }
    }, {
        key: 'render',
        value: function render() {
            _get(ThreeDVideo.prototype.__proto__ || Object.getPrototypeOf(ThreeDVideo.prototype), 'render', this).call(this);

            this._cameraL.target.x = 500 * Math.sin(this._phi) * Math.cos(this._theta);
            this._cameraL.target.y = 500 * Math.cos(this._phi);
            this._cameraL.target.z = 500 * Math.sin(this._phi) * Math.sin(this._theta);
            this._cameraL.lookAt(this._cameraL.target);

            if (this.VRMode) {
                var viewPortWidth = this._width / 2,
                    viewPortHeight = this._height;
                this._cameraR.target.x = 1000 + 500 * Math.sin(this._phi) * Math.cos(this._theta);
                this._cameraR.target.y = 500 * Math.cos(this._phi);
                this._cameraR.target.z = 500 * Math.sin(this._phi) * Math.sin(this._theta);
                this._cameraR.lookAt(this._cameraR.target);

                // render left eye
                this._renderer.setViewport(0, 0, viewPortWidth, viewPortHeight);
                this._renderer.setScissor(0, 0, viewPortWidth, viewPortHeight);
                this._renderer.render(this._scene, this._cameraL);

                // render right eye
                this._renderer.setViewport(viewPortWidth, 0, viewPortWidth, viewPortHeight);
                this._renderer.setScissor(viewPortWidth, 0, viewPortWidth, viewPortHeight);
                this._renderer.render(this._scene, this._cameraR);
            } else {
                this._renderer.render(this._scene, this._cameraL);
            }
        }
    }]);

    return ThreeDVideo;
}(_BaseCanvas3.default);

exports.default = ThreeDVideo;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./BaseCanvas":7}],20:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _Component2 = require('./Component');

var _Component3 = _interopRequireDefault(_Component2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Thumbnail = function (_Component) {
    _inherits(Thumbnail, _Component);

    function Thumbnail(player, options) {
        _classCallCheck(this, Thumbnail);

        var el = void 0;

        el = document.createElement('img');
        el.src = options.posterSrc;

        options.el = el;

        var _this = _possibleConstructorReturn(this, (Thumbnail.__proto__ || Object.getPrototypeOf(Thumbnail)).call(this, player, options));

        _this.one('load', function () {
            if (options.onComplete) {
                options.onComplete();
            }
        });
        return _this;
    }

    return Thumbnail;
}(_Component3.default);

exports.default = Thumbnail;

},{"./Component":10}],21:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _BaseCanvas2 = require('./BaseCanvas');

var _BaseCanvas3 = _interopRequireDefault(_BaseCanvas2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var TwoDVideo = function (_BaseCanvas) {
    _inherits(TwoDVideo, _BaseCanvas);

    function TwoDVideo(player, options, renderElement) {
        _classCallCheck(this, TwoDVideo);

        //define scene
        var _this = _possibleConstructorReturn(this, (TwoDVideo.__proto__ || Object.getPrototypeOf(TwoDVideo)).call(this, player, options, renderElement));

        _this._scene = new _three2.default.Scene();
        //define camera
        _this._camera = new _three2.default.PerspectiveCamera(_this.options.initFov, _this._width / _this._height, 1, 2000);
        _this._camera.target = new _three2.default.Vector3(0, 0, 0);
        return _this;
    }

    _createClass(TwoDVideo, [{
        key: 'enableVR',
        value: function enableVR() {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'enableVR', this).call(this);

            if (typeof window.vrHMD !== 'undefined') {
                var eyeParamsL = window.vrHMD.getEyeParameters('left');
                var eyeParamsR = window.vrHMD.getEyeParameters('right');

                this._eyeFOVL = eyeParamsL.recommendedFieldOfView;
                this._eyeFOVR = eyeParamsR.recommendedFieldOfView;
            }

            this._cameraL = new _three2.default.PerspectiveCamera(this._camera.fov, this._width / 2 / this._height, 1, 2000);
            this._cameraR = new _three2.default.PerspectiveCamera(this._camera.fov, this._width / 2 / this._height, 1, 2000);
            this._cameraL.target = new _three2.default.Vector3(0, 0, 0);
            this._cameraR.target = new _three2.default.Vector3(0, 0, 0);
        }
    }, {
        key: 'disableVR',
        value: function disableVR() {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'disableVR', this).call(this);
            this._renderer.setViewport(0, 0, this._width, this._height);
            this._renderer.setScissor(0, 0, this._width, this._height);
        }
    }, {
        key: 'handleResize',
        value: function handleResize() {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'handleResize', this).call(this);
            this._camera.aspect = this._width / this._height;
            this._camera.updateProjectionMatrix();
            if (this.VRMode) {
                this._cameraL.aspect = this._camera.aspect / 2;
                this._cameraR.aspect = this._camera.aspect / 2;
                this._cameraL.updateProjectionMatrix();
                this._cameraR.updateProjectionMatrix();
            }
        }
    }, {
        key: 'handleMouseWheel',
        value: function handleMouseWheel(event) {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'handleMouseWheel', this).call(this, event);

            // WebKit
            if (event.wheelDeltaY) {
                this._camera.fov -= event.wheelDeltaY * 0.05;
                // Opera / Explorer 9
            } else if (event.wheelDelta) {
                this._camera.fov -= event.wheelDelta * 0.05;
                // Firefox
            } else if (event.detail) {
                this._camera.fov += event.detail * 1.0;
            }
            this._camera.fov = Math.min(this.options.maxFov, this._camera.fov);
            this._camera.fov = Math.max(this.options.minFov, this._camera.fov);
            this._camera.updateProjectionMatrix();
            if (this.VRMode) {
                this._cameraL.fov = this._camera.fov;
                this._cameraR.fov = this._camera.fov;
                this._cameraL.updateProjectionMatrix();
                this._cameraR.updateProjectionMatrix();
            }
        }
    }, {
        key: 'handleTouchMove',
        value: function handleTouchMove(event) {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'handleTouchMove', this).call(this, event);

            if (this._isUserPinch) {
                var currentDistance = (0, _utils.getTouchesDistance)(event.touches);
                event.wheelDeltaY = (currentDistance - this._multiTouchDistance) * 2;
                this.handleMouseWheel(event);
                this._multiTouchDistance = currentDistance;
            }
        }
    }, {
        key: 'render',
        value: function render() {
            _get(TwoDVideo.prototype.__proto__ || Object.getPrototypeOf(TwoDVideo.prototype), 'render', this).call(this);

            this._camera.target.x = 500 * Math.sin(this._phi) * Math.cos(this._theta);
            this._camera.target.y = 500 * Math.cos(this._phi);
            this._camera.target.z = 500 * Math.sin(this._phi) * Math.sin(this._theta);
            this._camera.lookAt(this._camera.target);

            if (!this.VRMode) {
                this._renderer.render(this._scene, this._camera);
            } else {
                var viewPortWidth = this._width / 2,
                    viewPortHeight = this._height;
                if (typeof window.vrHMD !== 'undefined') {
                    this._cameraL.projectionMatrix = (0, _utils.fovToProjection)(this._eyeFOVL, true, this._camera.near, this._camera.far);
                    this._cameraR.projectionMatrix = (0, _utils.fovToProjection)(this._eyeFOVR, true, this._camera.near, this._camera.far);
                } else {
                    var lonL = this._lon + this.options.VRGapDegree;
                    var lonR = this._lon - this.options.VRGapDegree;

                    var thetaL = _three2.default.Math.degToRad(lonL);
                    var thetaR = _three2.default.Math.degToRad(lonR);

                    this._cameraL.target.x = 500 * Math.sin(this._phi) * Math.cos(thetaL);
                    this._cameraL.target.y = this._camera.target.y;
                    this._cameraL.target.z = 500 * Math.sin(this._phi) * Math.sin(thetaL);
                    this._cameraL.lookAt(this._cameraL.target);

                    this._cameraR.target.x = 500 * Math.sin(this._phi) * Math.cos(thetaR);
                    this._cameraR.target.y = this._camera.target.y;
                    this._cameraR.target.z = 500 * Math.sin(this._phi) * Math.sin(thetaR);
                    this._cameraR.lookAt(this._cameraR.target);
                }
                // render left eye
                this._renderer.setViewport(0, 0, viewPortWidth, viewPortHeight);
                this._renderer.setScissor(0, 0, viewPortWidth, viewPortHeight);
                this._renderer.render(this._scene, this._cameraL);

                // render right eye
                this._renderer.setViewport(viewPortWidth, 0, viewPortWidth, viewPortHeight);
                this._renderer.setScissor(viewPortWidth, 0, viewPortWidth, viewPortHeight);
                this._renderer.render(this._scene, this._cameraR);
            }
        }
    }]);

    return TwoDVideo;
}(_BaseCanvas3.default);

exports.default = TwoDVideo;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"../utils":36,"./BaseCanvas":7}],22:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _ThreeDVideo2 = require('./ThreeDVideo');

var _ThreeDVideo3 = _interopRequireDefault(_ThreeDVideo2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var VR1803D = function (_ThreeDVideo) {
    _inherits(VR1803D, _ThreeDVideo);

    function VR1803D(player, options, renderElement) {
        _classCallCheck(this, VR1803D);

        var _this = _possibleConstructorReturn(this, (VR1803D.__proto__ || Object.getPrototypeOf(VR1803D)).call(this, player, options, renderElement));

        var geometryL = new _three2.default.SphereBufferGeometry(500, 60, 40, 0, Math.PI).toNonIndexed();
        var geometryR = new _three2.default.SphereBufferGeometry(500, 60, 40, 0, Math.PI).toNonIndexed();

        var uvsL = geometryL.attributes.uv.array;
        var normalsL = geometryL.attributes.normal.array;
        for (var i = 0; i < normalsL.length / 3; i++) {
            uvsL[i * 2] = uvsL[i * 2] / 2;
        }

        var uvsR = geometryR.attributes.uv.array;
        var normalsR = geometryR.attributes.normal.array;
        for (var _i = 0; _i < normalsR.length / 3; _i++) {
            uvsR[_i * 2] = uvsR[_i * 2] / 2 + 0.5;
        }

        geometryL.scale(-1, 1, 1);
        geometryR.scale(-1, 1, 1);

        _this._meshL = new _three2.default.Mesh(geometryL, new _three2.default.MeshBasicMaterial({ map: _this._texture }));

        _this._meshR = new _three2.default.Mesh(geometryR, new _three2.default.MeshBasicMaterial({ map: _this._texture }));
        _this._meshR.position.set(1000, 0, 0);

        _this._scene.add(_this._meshL);
        return _this;
    }

    return VR1803D;
}(_ThreeDVideo3.default);

exports.default = VR1803D;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./ThreeDVideo":19}],23:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _ThreeDVideo2 = require('./ThreeDVideo');

var _ThreeDVideo3 = _interopRequireDefault(_ThreeDVideo2);

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var VR3603D = function (_ThreeDVideo) {
    _inherits(VR3603D, _ThreeDVideo);

    function VR3603D(player, options, renderElement) {
        _classCallCheck(this, VR3603D);

        var _this = _possibleConstructorReturn(this, (VR3603D.__proto__ || Object.getPrototypeOf(VR3603D)).call(this, player, options, renderElement));

        var geometryL = new _three2.default.SphereBufferGeometry(500, 60, 40).toNonIndexed();
        var geometryR = new _three2.default.SphereBufferGeometry(500, 60, 40).toNonIndexed();

        var uvsL = geometryL.attributes.uv.array;
        var normalsL = geometryL.attributes.normal.array;
        for (var i = 0; i < normalsL.length / 3; i++) {
            uvsL[i * 2 + 1] = uvsL[i * 2 + 1] / 2;
        }

        var uvsR = geometryR.attributes.uv.array;
        var normalsR = geometryR.attributes.normal.array;
        for (var _i = 0; _i < normalsR.length / 3; _i++) {
            uvsR[_i * 2 + 1] = uvsR[_i * 2 + 1] / 2 + 0.5;
        }

        geometryL.scale(-1, 1, 1);
        geometryR.scale(-1, 1, 1);

        _this._meshL = new _three2.default.Mesh(geometryL, new _three2.default.MeshBasicMaterial({ map: _this._texture }));

        _this._meshR = new _three2.default.Mesh(geometryR, new _three2.default.MeshBasicMaterial({ map: _this._texture }));
        _this._meshR.position.set(1000, 0, 0);

        _this._scene.add(_this._meshL);
        return _this;
    }

    return VR3603D;
}(_ThreeDVideo3.default);

exports.default = VR3603D;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./ThreeDVideo":19}],24:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _Button2 = require('./Button');

var _Button3 = _interopRequireDefault(_Button2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var VRButton = function (_Button) {
    _inherits(VRButton, _Button);

    function VRButton(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        _classCallCheck(this, VRButton);

        return _possibleConstructorReturn(this, (VRButton.__proto__ || Object.getPrototypeOf(VRButton)).call(this, player, options));
    }

    _createClass(VRButton, [{
        key: 'buildCSSClass',
        value: function buildCSSClass() {
            return 'vjs-VR-control ' + _get(VRButton.prototype.__proto__ || Object.getPrototypeOf(VRButton.prototype), 'buildCSSClass', this).call(this);
        }
    }, {
        key: 'handleClick',
        value: function handleClick(event) {
            _get(VRButton.prototype.__proto__ || Object.getPrototypeOf(VRButton.prototype), 'handleClick', this).call(this, event);
            this.toggleClass("enable");

            var videoCanvas = this.player.getComponent("VideoCanvas");
            var VRMode = videoCanvas.VRMode;
            !VRMode ? videoCanvas.enableVR() : videoCanvas.disableVR();
            !VRMode ? this.player.trigger('VRModeOn') : this.player.trigger('VRModeOff');
            if (!VRMode && this.options.VRFullscreen) {
                this.player.enableFullscreen();
            }
        }
    }]);

    return VRButton;
}(_Button3.default);

exports.default = VRButton;

},{"./Button":8}],25:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.VR180Defaults = exports.defaults = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _iphoneInlineVideo = require('iphone-inline-video');

var _iphoneInlineVideo2 = _interopRequireDefault(_iphoneInlineVideo);

var _wolfy87Eventemitter = require('wolfy87-eventemitter');

var _wolfy87Eventemitter2 = _interopRequireDefault(_wolfy87Eventemitter);

var _Equirectangular = require('./Components/Equirectangular');

var _Equirectangular2 = _interopRequireDefault(_Equirectangular);

var _Fisheye = require('./Components/Fisheye');

var _Fisheye2 = _interopRequireDefault(_Fisheye);

var _DualFisheye = require('./Components/DualFisheye');

var _DualFisheye2 = _interopRequireDefault(_DualFisheye);

var _VR3603D = require('./Components/VR3603D');

var _VR3603D2 = _interopRequireDefault(_VR3603D);

var _VR1803D = require('./Components/VR1803D');

var _VR1803D2 = _interopRequireDefault(_VR1803D);

var _Notification = require('./Components/Notification');

var _Notification2 = _interopRequireDefault(_Notification);

var _Thumbnail = require('./Components/Thumbnail');

var _Thumbnail2 = _interopRequireDefault(_Thumbnail);

var _VRButton = require('./Components/VRButton');

var _VRButton2 = _interopRequireDefault(_VRButton);

var _MarkerContainer = require('./Components/MarkerContainer');

var _MarkerContainer2 = _interopRequireDefault(_MarkerContainer);

var _Animation = require('./Components/Animation');

var _Animation2 = _interopRequireDefault(_Animation);

var _utils = require('./utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var runOnMobile = (0, _utils.mobileAndTabletcheck)();

var videoTypes = ["equirectangular", "fisheye", "dual_fisheye", "VR1803D", "VR3603D"];

var defaults = exports.defaults = {
    videoType: "equirectangular",
    MouseEnable: true,
    clickAndDrag: false,
    movingSpeed: {
        x: 0.0005,
        y: 0.0005
    },
    clickToToggle: true,
    scrollable: true,
    resizable: true,
    useHelperCanvas: "auto",
    initFov: 75,
    maxFov: 105,
    minFov: 51,
    //initial position for the video
    initLat: 0,
    initLon: 180,
    //A float value back to center when mouse out the canvas. The higher, the faster.
    returnLatSpeed: 0.5,
    returnLonSpeed: 2,
    backToInitLat: false,
    backToInitLon: false,

    //limit viewable zoom
    minLat: -85,
    maxLat: 85,

    minLon: 0,
    maxLon: 360,

    autoMobileOrientation: true,
    mobileVibrationValue: (0, _utils.isIos)() ? 0.022 : 1,

    VREnable: runOnMobile,
    VRGapDegree: 0.5,
    VRFullscreen: true, //auto fullscreen when in vr mode

    PanoramaThumbnail: false,
    KeyboardControl: false,
    KeyboardMovingSpeed: {
        x: 1,
        y: 1
    },

    Sphere: {
        rotateX: 0,
        rotateY: 0,
        rotateZ: 0
    },

    dualFish: {
        width: 1920,
        height: 1080,
        circle1: {
            x: 0.240625,
            y: 0.553704,
            rx: 0.23333,
            ry: 0.43148,
            coverX: 0.913,
            coverY: 0.9
        },
        circle2: {
            x: 0.757292,
            y: 0.553704,
            rx: 0.232292,
            ry: 0.4296296,
            coverX: 0.913,
            coverY: 0.9308
        }
    },

    Notice: {
        Enable: true,
        Message: "Please use your mouse drag and drop the video.",
        HideTime: 3000
    },

    Markers: false,

    Animations: false
};

var VR180Defaults = exports.VR180Defaults = {
    //initial position for the video
    initLat: 0,
    initLon: 90,
    //limit viewable zoom
    minLat: -75,
    maxLat: 55,

    minLon: 50,
    maxLon: 130,

    clickAndDrag: true
};

/**
 * panorama controller class which control required components
 */

var Panorama = function (_EventEmitter) {
    _inherits(Panorama, _EventEmitter);

    _createClass(Panorama, null, [{
        key: 'checkOptions',


        /**
         * check legacy option settings and produce warning message if user use legacy options, automatically set it to new options.
         * @param options the option settings which user parse.
         * @returns {*} the latest version which we use.
         */
        value: function checkOptions(options) {
            if (options.videoType === "3dVideo") {
                (0, _utils.warning)('videoType: ' + String(options.videoType) + ' is deprecated, please use VR3603D');
                options.videoType = "VR3603D";
            } else if (options.videoType && videoTypes.indexOf(options.videoType) === -1) {
                (0, _utils.warning)('videoType: ' + String(options.videoType) + ' is not supported, set video type to ' + String(defaults.videoType) + '.');
                options.videoType = defaults.videoType;
            }

            if (typeof options.backToVerticalCenter !== "undefined") {
                (0, _utils.warning)('backToVerticalCenter is deprecated, please use backToInitLat.');
                options.backToInitLat = options.backToVerticalCenter;
            }
            if (typeof options.backToHorizonCenter !== "undefined") {
                (0, _utils.warning)('backToHorizonCenter is deprecated, please use backToInitLon.');
                options.backToInitLon = options.backToHorizonCenter;
            }
            if (typeof options.returnStepLat !== "undefined") {
                (0, _utils.warning)('returnStepLat is deprecated, please use returnLatSpeed.');
                options.returnLatSpeed = options.returnStepLat;
            }
            if (typeof options.returnStepLon !== "undefined") {
                (0, _utils.warning)('returnStepLon is deprecated, please use returnLonSpeed.');
                options.returnLonSpeed = options.returnStepLon;
            }
            if (typeof options.helperCanvas !== "undefined") {
                (0, _utils.warning)('helperCanvas is deprecated, you don\'t have to set it up on new version.');
            }
            if (typeof options.callback !== "undefined") {
                (0, _utils.warning)('callback is deprecated, please use ready.');
                options.ready = options.callback;
            }
            if (typeof options.Sphere === "undefined") {
                options.Sphere = {};
            }
            if (typeof options.rotateX !== "undefined") {
                (0, _utils.warning)('rotateX is deprecated, please use Sphere:{ rotateX: 0, rotateY: 0, rotateZ: 0}.');
                if (options.Sphere) {
                    options.Sphere.rotateX = options.rotateX;
                }
            }
            if (typeof options.rotateY !== "undefined") {
                (0, _utils.warning)('rotateY is deprecated, please use Sphere:{ rotateX: 0, rotateY: 0, rotateZ: 0}.');
                if (options.Sphere) {
                    options.Sphere.rotateY = options.rotateY;
                }
            }
            if (typeof options.rotateZ !== "undefined") {
                (0, _utils.warning)('rotateZ is deprecated, please use Sphere:{ rotateX: 0, rotateY: 0, rotateZ: 0}.');
                if (options.Sphere) {
                    options.Sphere.rotateY = options.rotateZ;
                }
            }
            if (typeof options.Notice === "undefined") {
                options.Notice = {};
            }
            if (typeof options.showNotice !== "undefined") {
                (0, _utils.warning)('showNotice is deprecated, please use Notice: { Enable: true }');
                if (options.Notice) {
                    options.Notice.Enable = options.showNotice;
                }
            }
            if (typeof options.NoticeMessage !== "undefined") {
                (0, _utils.warning)('NoticeMessage is deprecated, please use Notice: { Message: "" }');
                if (options.Notice) {
                    options.Notice.Message = options.NoticeMessage;
                }
            }
            if (typeof options.autoHideNotice !== "undefined") {
                (0, _utils.warning)('autoHideNotice is deprecated, please use Notice: { HideTime: 3000 }');
                if (options.Notice) {
                    options.Notice.HideTime = options.autoHideNotice;
                }
            }
        }
    }, {
        key: 'chooseVideoComponent',
        value: function chooseVideoComponent(videoType) {
            var VideoClass = void 0;
            switch (videoType) {
                case "equirectangular":
                    VideoClass = _Equirectangular2.default;
                    break;
                case "fisheye":
                    VideoClass = _Fisheye2.default;
                    break;
                case "dual_fisheye":
                    VideoClass = _DualFisheye2.default;
                    break;
                case "VR3603D":
                    VideoClass = _VR3603D2.default;
                    break;
                case "VR1803D":
                    VideoClass = _VR1803D2.default;
                    break;
                default:
                    VideoClass = _Equirectangular2.default;
            }
            return VideoClass;
        }
    }]);

    function Panorama(player) {
        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        _classCallCheck(this, Panorama);

        var _this = _possibleConstructorReturn(this, (Panorama.__proto__ || Object.getPrototypeOf(Panorama)).call(this));

        Panorama.checkOptions(options);
        if (options.videoType === "VR1803D") {
            options = (0, _utils.mergeOptions)({}, VR180Defaults, options);
        }
        _this._options = (0, _utils.mergeOptions)({}, defaults, options);
        _this._player = player;

        _this.player.addClass("vjs-panorama");

        if (!_utils.Detector.webgl) {
            _this.popupNotification((0, _utils.webGLErrorMessage)());
            return _possibleConstructorReturn(_this);
        }

        var VideoClass = Panorama.chooseVideoComponent(_this.options.videoType);
        //render 360 thumbnail
        if (_this.options.PanoramaThumbnail && player.getThumbnailURL()) {
            var thumbnailURL = player.getThumbnailURL();
            var poster = new _Thumbnail2.default(player, {
                posterSrc: thumbnailURL,
                onComplete: function onComplete() {
                    if (_this.thumbnailCanvas) {
                        _this.thumbnailCanvas._texture.needsUpdate = true;
                        _this.thumbnailCanvas.startAnimation();
                    }
                }
            });
            _this.player.addComponent("Thumbnail", poster);

            poster.el().style.display = "none";
            _this._thumbnailCanvas = new VideoClass(player, _this.options, poster.el());
            _this.player.addComponent("ThumbnailCanvas", _this.thumbnailCanvas);

            _this.player.one("play", function () {
                _this.thumbnailCanvas && _this.thumbnailCanvas.hide();
                _this.player.removeComponent("Thumbnail");
                _this.player.removeComponent("ThumbnailCanvas");
                _this._thumbnailCanvas = null;
            });
        }

        //enable inline play on mobile
        if (runOnMobile) {
            var videoElement = _this.player.getVideoEl();
            if ((0, _utils.isRealIphone)()) {
                //ios 10 support play video inline
                videoElement.setAttribute("playsinline", "");
                (0, _iphoneInlineVideo2.default)(videoElement, true);
            }
            _this.player.addClass("vjs-panorama-mobile-inline-video");
            //by default videojs hide control bar on mobile device.
            _this.player.removeClass("vjs-using-native-controls");
        }

        //add vr icon to player
        if (_this.options.VREnable) {
            var controlbar = _this.player.controlBar();
            var index = controlbar.childNodes.length;
            var vrButton = new _VRButton2.default(player, _this.options);
            vrButton.disable();
            _this.player.addComponent("VRButton", vrButton, _this.player.controlBar(), index - 1);
        }

        _this.player.ready(function () {
            //add canvas to player
            _this._videoCanvas = new VideoClass(player, _this.options, player.getVideoEl());
            _this.videoCanvas.hide();
            _this.player.addComponent("VideoCanvas", _this.videoCanvas);

            _this.attachEvents();

            if (_this.options.VREnable) {
                var _vrButton = _this.player.getComponent("VRButton");
                _vrButton && _vrButton.enable();
            }

            if (_this.options.ready) {
                _this.options.ready.call(_this);
            }
        });

        //register trigger callback function, so everything trigger to player will also trigger in here
        _this.player.registerTriggerCallback(function (eventName) {
            _this.trigger(eventName);
        });
        return _this;
    }

    _createClass(Panorama, [{
        key: 'dispose',
        value: function dispose() {
            this.detachEvents();
            this.player.getVideoEl().style.visibility = "visible";
            this.player.removeComponent("VideoCanvas");
        }
    }, {
        key: 'attachEvents',
        value: function attachEvents() {
            var _this2 = this;

            //show notice message
            if (this.options.Notice && this.options.Notice.Enable) {
                this.player.one("playing", function () {
                    var message = _this2.options.Notice && _this2.options.Notice.Message || "";
                    _this2.popupNotification(message);
                });
            }

            //enable canvas rendering when video is playing
            var handlePlay = function handlePlay() {
                _this2.player.getVideoEl().style.visibility = "hidden";
                _this2.videoCanvas.startAnimation();
                _this2.videoCanvas.show();

                //initial markers
                if (_this2.options.Markers && Array.isArray(_this2.options.Markers)) {
                    var markerContainer = new _MarkerContainer2.default(_this2.player, {
                        canvas: _this2.videoCanvas,
                        markers: _this2.options.Markers,
                        VREnable: _this2.options.VREnable
                    });
                    _this2.player.addComponent("markerContainer", markerContainer);
                }

                //initial animations
                if (_this2.options.Animation && Array.isArray(_this2.options.Animation)) {
                    _this2._animation = new _Animation2.default(_this2.player, {
                        animation: _this2.options.Animation,
                        canvas: _this2.videoCanvas
                    });
                }

                //detect black screen
                if (window.console && window.console.error) {
                    (function () {
                        var originalErrorFunction = window.console.error;
                        var originalWarnFunction = window.console.warn;
                        window.console.error = function (error) {
                            if (error.message.indexOf("insecure") !== -1) {
                                _this2.popupNotification((0, _utils.crossDomainWarning)());
                                _this2.dispose();
                            }
                        };
                        window.console.warn = function (warn) {
                            if (warn.indexOf("gl.getShaderInfoLog") !== -1) {
                                _this2.popupNotification((0, _utils.crossDomainWarning)());
                                _this2.dispose();
                                window.console.warn = originalWarnFunction;
                            }
                        };
                        setTimeout(function () {
                            window.console.error = originalErrorFunction;
                            window.console.warn = originalWarnFunction;
                        }, 500);
                    })();
                }
            };
            if (!this.player.paused()) {
                handlePlay();
            } else {
                this.player.one("play", handlePlay);
            }

            var report = function report() {
                _this2.player.reportUserActivity();
            };

            this.videoCanvas.addListeners({
                "touchMove": report,
                "tap": report
            });
        }
    }, {
        key: 'detachEvents',
        value: function detachEvents() {
            if (this.thumbnailCanvas) {
                this.thumbnailCanvas.stopAnimation();
            }
            if (this.videoCanvas) {
                this.videoCanvas.stopAnimation();
            }
        }
    }, {
        key: 'popupNotification',
        value: function popupNotification(message) {
            var notice = this.player.addComponent("Notice", new _Notification2.default(this.player, {
                Message: message
            }));

            if (this.options.Notice && this.options.Notice.HideTime && this.options.Notice.HideTime > 0) {
                setTimeout(function () {
                    notice.removeClass("vjs-video-notice-show");
                    notice.addClass("vjs-video-notice-fadeOut");
                    notice.one(_utils.transitionEvent, function () {
                        notice.hide();
                        notice.removeClass("vjs-video-notice-fadeOut");
                    });
                }, this.options.Notice.HideTime);
            }
        }
    }, {
        key: 'addTimeline',
        value: function addTimeline(animation) {
            this._animation.addTimeline(animation);
        }
    }, {
        key: 'enableAnimation',
        value: function enableAnimation() {
            this._animation.attachEvents();
        }
    }, {
        key: 'disableAnimation',
        value: function disableAnimation() {
            this._animation.detachEvents();
        }
    }, {
        key: 'getCoordinates',
        value: function getCoordinates() {
            var canvas = this.thumbnailCanvas || this.videoCanvas;
            return {
                lat: canvas._lat,
                lon: canvas._lon
            };
        }
    }, {
        key: 'thumbnailCanvas',
        get: function get() {
            return this._thumbnailCanvas;
        }
    }, {
        key: 'videoCanvas',
        get: function get() {
            return this._videoCanvas;
        }
    }, {
        key: 'player',
        get: function get() {
            return this._player;
        }
    }, {
        key: 'options',
        get: function get() {
            return this._options;
        }
    }]);

    return Panorama;
}(_wolfy87Eventemitter2.default);

exports.default = Panorama;

},{"./Components/Animation":6,"./Components/DualFisheye":11,"./Components/Equirectangular":12,"./Components/Fisheye":13,"./Components/MarkerContainer":16,"./Components/Notification":18,"./Components/Thumbnail":20,"./Components/VR1803D":22,"./Components/VR3603D":23,"./Components/VRButton":24,"./utils":36,"iphone-inline-video":3,"wolfy87-eventemitter":5}],26:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _Loader = require('./tech/Loader');

var _Loader2 = _interopRequireDefault(_Loader);

var _Panorama = require('./Panorama');

var _Panorama2 = _interopRequireDefault(_Panorama);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var playerClass = (0, _Loader2.default)(window.VIDEO_PANORAMA);

if (playerClass) {
    playerClass.registerPlugin();
} else {
    throw new Error("Could not found support player.");
}

var plugin = function plugin(playerDom, options) {
    var videoEm = typeof playerDom === "string" ? document.querySelector(playerDom) : playerDom;
    if (playerClass) {
        // $FlowFixMe
        var player = new playerClass(videoEm, options);
        var panorama = new _Panorama2.default(player, options);
        return panorama;
    }
};

window.Panorama = plugin;

exports.default = plugin;

},{"./Panorama":25,"./tech/Loader":28}],27:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

// @ flow

var BasePlayer = function () {
    function BasePlayer(playerInstance) {
        _classCallCheck(this, BasePlayer);

        if (Object.getPrototypeOf(this) === BasePlayer.prototype) {
            throw Error('abstract class should not be instantiated directly; write a subclass');
        }

        this.playerInstance = playerInstance;
        this._components = [];
    }

    _createClass(BasePlayer, [{
        key: 'registerTriggerCallback',
        value: function registerTriggerCallback(callback) {
            this._triggerCallback = callback;
        }
    }, {
        key: 'el',
        value: function el() {
            throw Error('Not implemented');
        }
    }, {
        key: 'getVideoEl',
        value: function getVideoEl() {
            throw Error('Not implemented');
        }
    }, {
        key: 'getThumbnailURL',
        value: function getThumbnailURL() {
            throw Error('Not implemented');
        }
    }, {
        key: 'on',
        value: function on() {
            throw Error('Not implemented');
        }
    }, {
        key: 'off',
        value: function off() {
            throw Error('Not implemented');
        }
    }, {
        key: 'one',
        value: function one() {
            throw Error('Not implemented');
        }
    }, {
        key: 'trigger',
        value: function trigger(name) {
            throw Error('Not implemented');
        }
    }, {
        key: 'addClass',
        value: function addClass(name) {
            throw Error('Not implemented');
        }
    }, {
        key: 'removeClass',
        value: function removeClass(name) {
            throw Error('Not implemented');
        }
    }, {
        key: 'addComponent',
        value: function addComponent(name, component, location, index) {
            if (!location) {
                location = this.el();
            }
            if (!index) {
                index = -1;
            }

            if (typeof component.el === "function" && component.el()) {
                if (index === -1) {
                    location.appendChild(component.el());
                } else {
                    var children = location.childNodes;
                    var child = children[index];
                    location.insertBefore(component.el(), child);
                }
            }

            this._components.push({
                name: name,
                component: component,
                location: location
            });

            return component;
        }
    }, {
        key: 'removeComponent',
        value: function removeComponent(name) {
            this._components = this._components.reduce(function (acc, component) {
                if (component.name !== name) {
                    acc.push(component);
                } else {
                    component.component.dispose();
                }
                return acc;
            }, []);
        }
    }, {
        key: 'getComponent',
        value: function getComponent(name) {
            var componentData = void 0;
            for (var i = 0; i < this._components.length; i++) {
                if (this._components[i].name === name) {
                    componentData = this._components[i];
                    break;
                }
            }
            return componentData ? componentData.component : null;
        }
    }, {
        key: 'play',
        value: function play() {
            this.playerInstance.play();
        }
    }, {
        key: 'pause',
        value: function pause() {
            this.playerInstance.pause();
        }
    }, {
        key: 'paused',
        value: function paused() {
            throw Error('Not implemented');
        }
    }, {
        key: 'readyState',
        value: function readyState() {
            throw Error('Not implemented');
        }
    }, {
        key: 'reportUserActivity',
        value: function reportUserActivity() {
            throw Error('Not implemented');
        }
    }, {
        key: 'controlBar',
        value: function controlBar() {
            throw Error('Not implemented');
        }
    }, {
        key: 'enableFullscreen',
        value: function enableFullscreen() {
            throw Error('Not implemented');
        }
    }, {
        key: 'ready',
        value: function ready(fn) {
            throw Error('Not implemented');
        }
    }, {
        key: 'components',
        get: function get() {
            return this._components;
        }
    }], [{
        key: 'registerPlugin',
        value: function registerPlugin() {
            throw Error('Not implemented');
        }
    }]);

    return BasePlayer;
}();

exports.default = BasePlayer;

},{}],28:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _Videojs = require('./Videojs4');

var _Videojs2 = _interopRequireDefault(_Videojs);

var _Videojs3 = require('./Videojs5');

var _Videojs4 = _interopRequireDefault(_Videojs3);

var _MediaElementPlayer = require('./MediaElementPlayer');

var _MediaElementPlayer2 = _interopRequireDefault(_MediaElementPlayer);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var VIDEOPLAYER = {
    'videojs_v4': _Videojs2.default,
    'videojs_v5': _Videojs4.default,
    'MediaElementPlayer': _MediaElementPlayer2.default
};

function checkType(playerType) {
    if (typeof playerType !== "undefined") {
        if (VIDEOPLAYER[playerType]) {
            return VIDEOPLAYER[playerType];
        }
        (0, _utils.warning)('playerType: ' + playerType + ' is not supported');
    }
    return null;
}

function chooseTech() {
    if (typeof window.videojs !== "undefined") {
        var version = window.videojs.VERSION;
        var major = (0, _utils.getVideojsVersion)(version);
        if (major === 4) {
            return VIDEOPLAYER['videojs_v4'];
        } else {
            return VIDEOPLAYER['videojs_v5'];
        }
    }

    if (typeof window.MediaElementPlayer !== "undefined") {
        return VIDEOPLAYER["MediaElementPlayer"];
    }

    return null;
}

function Loader(playerType) {
    var preferType = checkType(playerType);
    if (!preferType) {
        preferType = chooseTech();
    }

    return preferType;
}

exports.default = Loader;

},{"../utils":36,"./MediaElementPlayer":29,"./Videojs4":30,"./Videojs5":31}],29:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _Panorama = require('../Panorama');

var _Panorama2 = _interopRequireDefault(_Panorama);

var _utils = require('../utils');

var _BasePlayer2 = require('./BasePlayer');

var _BasePlayer3 = _interopRequireDefault(_BasePlayer2);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } // @ flow

var MediaElement = function (_BasePlayer) {
    _inherits(MediaElement, _BasePlayer);

    function MediaElement(playerInstance) {
        _classCallCheck(this, MediaElement);

        var _this = _possibleConstructorReturn(this, (MediaElement.__proto__ || Object.getPrototypeOf(MediaElement)).call(this, playerInstance));

        if ((0, _utils.isIos)()) {
            _this._fullscreenOnIOS();
        }
        return _this;
    }

    _createClass(MediaElement, [{
        key: 'el',
        value: function el() {
            return this.playerInstance.container;
        }
    }, {
        key: 'getVideoEl',
        value: function getVideoEl() {
            return this.playerInstance.domNode;
        }
    }, {
        key: 'getThumbnailURL',
        value: function getThumbnailURL() {
            return this.playerInstance.options.poster || this.getVideoEl().getAttribute("poster");
        }
    }, {
        key: 'addClass',
        value: function addClass(name) {
            this.playerInstance.container.classList.add(name);
        }
    }, {
        key: 'removeClass',
        value: function removeClass(name) {
            this.playerInstance.container.classList.remove(name);
        }
    }, {
        key: 'on',
        value: function on() {
            var name = arguments.length <= 0 ? undefined : arguments[0];
            var fn = arguments.length <= 1 ? undefined : arguments[1];
            this.getVideoEl().addEventListener(name, fn);
        }
    }, {
        key: 'off',
        value: function off() {
            var name = arguments.length <= 0 ? undefined : arguments[0];
            var fn = arguments.length <= 1 ? undefined : arguments[1];
            this.getVideoEl().removeEventListener(name, fn);
        }
    }, {
        key: 'one',
        value: function one() {
            var _this2 = this;

            var name = arguments.length <= 0 ? undefined : arguments[0];
            var fn = arguments.length <= 1 ? undefined : arguments[1];
            var _oneTimeFunction = void 0;
            this.on(name, _oneTimeFunction = function oneTimeFunction() {
                fn();
                _this2.off(name, _oneTimeFunction);
            });
        }
    }, {
        key: 'trigger',
        value: function trigger(name) {
            var event = (0, _utils.customEvent)(name, this.el());
            this.getVideoEl().dispatchEvent(event);
            if (this._triggerCallback) {
                this._triggerCallback(name);
            }
        }
    }, {
        key: 'paused',
        value: function paused() {
            return this.getVideoEl().paused;
        }
    }, {
        key: 'readyState',
        value: function readyState() {
            return this.getVideoEl().readyState;
        }
    }, {
        key: 'reportUserActivity',
        value: function reportUserActivity() {
            this.playerInstance.showControls();
        }
    }, {
        key: 'controlBar',
        value: function controlBar() {
            return this.playerInstance.controls;
        }
    }, {
        key: 'enableFullscreen',
        value: function enableFullscreen() {
            if (!this.playerInstance.isFullScreen) {
                this.playerInstance.enterFullScreen();
            }
        }
    }, {
        key: '_resizeCanvasFn',
        value: function _resizeCanvasFn(canvas) {
            var _this3 = this;

            return function () {
                _this3.playerInstance.container.style.width = "100%";
                _this3.playerInstance.container.style.height = "100%";
                canvas.handleResize();
            };
        }
    }, {
        key: '_fullscreenOnIOS',
        value: function _fullscreenOnIOS() {
            var self = this;
            //disable fullscreen on ios
            this.playerInstance.enterFullScreen = function () {
                var canvas = self.getComponent("VideoCanvas");
                var resizeFn = self._resizeCanvasFn(canvas).bind(self);
                self.trigger("before_EnterFullscreen");
                document.documentElement.classList.add(this.options.classPrefix + 'fullscreen');
                self.addClass(this.options.classPrefix + 'container-fullscreen');
                this.container.style.width = "100%";
                this.container.style.height = "100%";
                window.addEventListener("devicemotion", resizeFn); //trigger when user rotate screen
                self.trigger("after_EnterFullscreen");
                this.isFullScreen = true;
                canvas.handleResize();
            };

            this.playerInstance.exitFullScreen = function () {
                var canvas = self.getComponent("VideoCanvas");
                var resizeFn = self._resizeCanvasFn(canvas).bind(self);
                self.trigger("before_ExitFullscreen");
                document.documentElement.classList.remove(this.options.classPrefix + 'fullscreen');
                self.removeClass(this.options.classPrefix + 'container-fullscreen');
                this.isFullScreen = false;
                this.container.style.width = "";
                this.container.style.height = "";
                window.removeEventListener("devicemotion", resizeFn);
                self.trigger("after_ExitFullscreen");
                canvas.handleResize();
            };
        }
    }, {
        key: 'ready',
        value: function ready(fn) {
            this.one('canplay', fn);
        }
    }], [{
        key: 'registerPlugin',
        value: function registerPlugin() {
            mejs.MepDefaults = (0, _utils.mergeOptions)(mejs.MepDefaults, {
                Panorama: _extends({}, _Panorama.defaults)
            });
            MediaElementPlayer.prototype = (0, _utils.mergeOptions)(MediaElementPlayer.prototype, {
                buildPanorama: function buildPanorama(player) {
                    if (player.domNode.tagName.toLowerCase() !== "video") {
                        throw new Error("Panorama don't support third party player");
                    }
                    var instance = new MediaElement(player);
                    player.panorama = new _Panorama2.default(instance, this.options.Panorama);
                },
                clearPanorama: function clearPanorama(player) {
                    if (player.panorama) {
                        player.panorama.dispose();
                    }
                }
            });
        }
    }]);

    return MediaElement;
}(_BasePlayer3.default);

exports.default = MediaElement;

},{"../Panorama":25,"../utils":36,"./BasePlayer":27}],30:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _video = (typeof window !== "undefined" ? window['videojs'] : typeof global !== "undefined" ? global['videojs'] : null);

var _video2 = _interopRequireDefault(_video);

var _videojs = require('./videojs');

var _videojs2 = _interopRequireDefault(_videojs);

var _Panorama = require('../Panorama');

var _Panorama2 = _interopRequireDefault(_Panorama);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Videojs4 = function (_BaseVideoJs) {
    _inherits(Videojs4, _BaseVideoJs);

    function Videojs4() {
        _classCallCheck(this, Videojs4);

        return _possibleConstructorReturn(this, (Videojs4.__proto__ || Object.getPrototypeOf(Videojs4)).apply(this, arguments));
    }

    _createClass(Videojs4, [{
        key: 'getVideoEl',
        value: function getVideoEl() {
            return this.playerInstance.tech ? this.playerInstance.tech.el() : this.playerInstance.h.el();
        }
    }, {
        key: '_originalFullscreenClickFn',
        value: function _originalFullscreenClickFn() {
            return this.playerInstance.controlBar.fullscreenToggle.onClick || this.playerInstance.controlBar.fullscreenToggle.u;
        }
    }], [{
        key: 'registerPlugin',
        value: function registerPlugin() {
            _video2.default.plugin("panorama", function (options) {
                var instance = new Videojs4(this);
                var panorama = new _Panorama2.default(instance, options);
                return panorama;
            });
        }
    }]);

    return Videojs4;
}(_videojs2.default);

exports.default = Videojs4;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"../Panorama":25,"./videojs":32}],31:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _video = (typeof window !== "undefined" ? window['videojs'] : typeof global !== "undefined" ? global['videojs'] : null);

var _video2 = _interopRequireDefault(_video);

var _videojs = require('./videojs');

var _videojs2 = _interopRequireDefault(_videojs);

var _Panorama = require('../Panorama');

var _Panorama2 = _interopRequireDefault(_Panorama);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Videojs5 = function (_BaseVideoJs) {
    _inherits(Videojs5, _BaseVideoJs);

    function Videojs5() {
        _classCallCheck(this, Videojs5);

        return _possibleConstructorReturn(this, (Videojs5.__proto__ || Object.getPrototypeOf(Videojs5)).apply(this, arguments));
    }

    _createClass(Videojs5, [{
        key: 'getVideoEl',
        value: function getVideoEl() {
            return this.playerInstance.tech({ IWillNotUseThisInPlugins: true }).el();
        }
    }, {
        key: '_originalFullscreenClickFn',
        value: function _originalFullscreenClickFn() {
            return this.playerInstance.controlBar.fullscreenToggle.handleClick;
        }
    }], [{
        key: 'registerPlugin',
        value: function registerPlugin() {
            _video2.default.plugin("panorama", function (options) {
                var instance = new Videojs5(this);
                var panorama = new _Panorama2.default(instance, options);
                return panorama;
            });
        }
    }]);

    return Videojs5;
}(_videojs2.default);

exports.default = Videojs5;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"../Panorama":25,"./videojs":32}],32:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _BasePlayer2 = require('./BasePlayer');

var _BasePlayer3 = _interopRequireDefault(_BasePlayer2);

var _Component = require('../Components/Component');

var _Component2 = _interopRequireDefault(_Component);

var _utils = require('../utils');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Videojs = function (_BasePlayer) {
    _inherits(Videojs, _BasePlayer);

    function Videojs(playerInstance) {
        _classCallCheck(this, Videojs);

        //ios device don't support fullscreen, we have to monkey patch the original fullscreen function.
        var _this = _possibleConstructorReturn(this, (Videojs.__proto__ || Object.getPrototypeOf(Videojs)).call(this, playerInstance));

        if ((0, _utils.isIos)()) {
            _this._fullscreenOnIOS();
        }
        //resize video if fullscreen change, this is used for ios device
        _this.on("fullscreenchange", function () {
            var canvas = _this.getComponent("VideoCanvas");
            canvas.handleResize();
        });
        return _this;
    }

    _createClass(Videojs, [{
        key: 'el',
        value: function el() {
            return this.playerInstance.el();
        }
    }, {
        key: 'getVideoEl',
        value: function getVideoEl() {
            throw Error('Not implemented');
        }
    }, {
        key: 'getThumbnailURL',
        value: function getThumbnailURL() {
            return this.playerInstance.poster();
        }
    }, {
        key: 'on',
        value: function on() {
            var _playerInstance;

            (_playerInstance = this.playerInstance).on.apply(_playerInstance, arguments);
        }
    }, {
        key: 'off',
        value: function off() {
            var _playerInstance2;

            (_playerInstance2 = this.playerInstance).off.apply(_playerInstance2, arguments);
        }
    }, {
        key: 'one',
        value: function one() {
            var _playerInstance3;

            (_playerInstance3 = this.playerInstance).one.apply(_playerInstance3, arguments);
        }
    }, {
        key: 'addClass',
        value: function addClass(name) {
            this.playerInstance.addClass(name);
        }
    }, {
        key: 'removeClass',
        value: function removeClass(name) {
            this.playerInstance.removeClass(name);
        }
    }, {
        key: '_resizeCanvasFn',
        value: function _resizeCanvasFn(canvas) {
            return function () {
                canvas.handleResize();
            };
        }
    }, {
        key: 'paused',
        value: function paused() {
            return this.playerInstance.paused();
        }
    }, {
        key: 'readyState',
        value: function readyState() {
            return this.playerInstance.readyState();
        }
    }, {
        key: 'trigger',
        value: function trigger(name) {
            this.playerInstance.trigger(name);
            if (this._triggerCallback) {
                this._triggerCallback(name);
            }
        }
    }, {
        key: 'reportUserActivity',
        value: function reportUserActivity() {
            this.playerInstance.reportUserActivity();
        }

        /**
         * Get original fullscreen function
         */

    }, {
        key: '_originalFullscreenClickFn',
        value: function _originalFullscreenClickFn() {
            throw Error('Not implemented');
        }
    }, {
        key: '_fullscreenOnIOS',
        value: function _fullscreenOnIOS() {
            var _this2 = this;

            this.playerInstance.controlBar.fullscreenToggle.off("tap", this._originalFullscreenClickFn());
            this.playerInstance.controlBar.fullscreenToggle.on("tap", function () {
                var canvas = _this2.getComponent("VideoCanvas");
                var resizeFn = _this2._resizeCanvasFn(canvas);
                if (!_this2.playerInstance.isFullscreen()) {
                    _this2.trigger("before_EnterFullscreen");
                    //set to fullscreen
                    _this2.playerInstance.isFullscreen(true);
                    _this2.playerInstance.enterFullWindow();
                    window.addEventListener("devicemotion", resizeFn); //trigger when user rotate screen
                    _this2.trigger("after_EnterFullscreen");
                } else {
                    _this2.trigger("before_ExitFullscreen");
                    _this2.playerInstance.isFullscreen(false);
                    _this2.playerInstance.exitFullWindow();
                    window.removeEventListener("devicemotion", resizeFn);
                    _this2.trigger("after_ExitFullscreen");
                }
                _this2.trigger("fullscreenchange");
            });
        }
    }, {
        key: 'controlBar',
        value: function controlBar() {
            var controlBar = this.playerInstance.controlBar;
            return controlBar.el();
        }
    }, {
        key: 'enableFullscreen',
        value: function enableFullscreen() {
            if (!this.playerInstance.isFullscreen()) this.playerInstance.controlBar.fullscreenToggle.trigger("tap");
        }
    }, {
        key: 'ready',
        value: function ready(fn) {
            this.playerInstance.ready(fn);
        }
    }]);

    return Videojs;
}(_BasePlayer3.default);

exports.default = Videojs;

},{"../Components/Component":10,"../utils":36,"./BasePlayer":27}],33:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
function whichTransitionEvent() {
    var el = document.createElement('div');
    var transitions = {
        'transition': 'transitionend',
        'OTransition': 'oTransitionEnd',
        'MozTransition': 'transitionend',
        'WebkitTransition': 'webkitTransitionEnd'
    };

    for (var t in transitions) {
        // $FlowFixMe
        if (el.style[t] !== undefined) {
            return transitions[t];
        }
    }
}

var transitionEvent = exports.transitionEvent = whichTransitionEvent();

//adopt from http://gizma.com/easing/
function linear(t, b, c, d) {
    return c * t / d + b;
}

function easeInQuad(t, b, c, d) {
    t /= d;
    return c * t * t + b;
}

function easeOutQuad(t, b, c, d) {
    t /= d;
    return -c * t * (t - 2) + b;
}

function easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
}

var easeFunctions = exports.easeFunctions = {
    linear: linear,
    easeInQuad: easeInQuad,
    easeOutQuad: easeOutQuad,
    easeInOutQuad: easeInOutQuad
};

},{}],34:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.webGLErrorMessage = webGLErrorMessage;
exports.ieOrEdgeVersion = ieOrEdgeVersion;
exports.isLiveStreamOnSafari = isLiveStreamOnSafari;
exports.supportVideoTexture = supportVideoTexture;

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var _Detector = function _Detector() {
    _classCallCheck(this, _Detector);

    this.canvas = !!window.CanvasRenderingContext2D;
    this.webgl = false;
    try {
        this.canvas = document.createElement("canvas");
        this.webgl = !!(window.WebGLRenderingContext && (this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl')));
    } catch (e) {}
    this.workers = !!window.Worker;
    this.fileapi = window.File && window.FileReader && window.FileList && window.Blob;
};

var Detector = exports.Detector = new _Detector();

function webGLErrorMessage() {
    var element = document.createElement('div');
    element.id = 'webgl-error-message';

    if (!Detector.webgl) {
        element.innerHTML = window.WebGLRenderingContext ? ['Your graphics card does not seem to support <a href="http://khronos.org/webgl/wiki/Getting_a_WebGL_Implementation" style="color:#000">WebGL</a>.<br />', 'Find out how to get it <a href="http://get.webgl.org/" style="color:#000">here</a>.'].join('\n') : ['Your browser does not seem to support <a href="http://khronos.org/webgl/wiki/Getting_a_WebGL_Implementation" style="color:#000">WebGL</a>.<br/>', 'Find out how to get it <a href="http://get.webgl.org/" style="color:#000">here</a>.'].join('\n');
    }
    return element;
}

/**
 * check ie or edge browser version, return -1 if use other browsers
 */
function ieOrEdgeVersion() {
    var rv = -1;
    if (navigator.appName === 'Microsoft Internet Explorer') {

        var ua = navigator.userAgent,
            re = new RegExp("MSIE ([0-9]{1,}[\\.0-9]{0,})");

        if (re.exec(ua) !== null) {
            // $FlowFixMe: suppressing this error, RegExp don't support static property
            rv = parseFloat(RegExp.$1);
        }
    } else if (navigator.appName === "Netscape") {
        /// in IE 11 the navigator.appVersion says 'trident'
        /// in Edge the navigator.appVersion does not say trident
        if (navigator.appVersion.indexOf('Trident') !== -1) rv = 11;else {
            var _ua = navigator.userAgent;
            var _re = new RegExp("Edge\/([0-9]{1,}[\\.0-9]{0,})");
            if (_re.exec(_ua) !== null) {
                // $FlowFixMe
                rv = parseFloat(RegExp.$1);
            }
        }
    }

    return rv;
}

function isLiveStreamOnSafari(videoElement) {
    //live stream on safari doesn't support video texture
    var videoSources = [].slice.call(videoElement.querySelectorAll("source"));
    var result = false;
    if (videoElement.src && videoElement.src.indexOf('.m3u8') > -1) {
        videoSources.push({
            src: videoElement.src,
            type: "application/x-mpegURL"
        });
    }
    for (var i = 0; i < videoSources.length; i++) {
        var currentVideoSource = videoSources[i];
        if ((currentVideoSource.type === "application/x-mpegURL" || currentVideoSource.type === "application/vnd.apple.mpegurl") && /(Safari|AppleWebKit)/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor)) {
            result = true;
            break;
        }
    }
    return result;
}

function supportVideoTexture(videoElement) {
    //ie 11 and edge 12 and live stream on safari doesn't support video texture directly.
    var version = ieOrEdgeVersion();
    return (version === -1 || version >= 13) && !isLiveStreamOnSafari(videoElement);
}

},{}],35:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.customEvent = customEvent;
function customEvent(eventName, target) {
    var event = new CustomEvent(eventName, {
        'detail': {
            target: target
        }
    });
    return event;
}

},{}],36:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _mergeOptions = require('./merge-options');

Object.keys(_mergeOptions).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _mergeOptions[key];
    }
  });
});

var _warning = require('./warning');

Object.keys(_warning).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _warning[key];
    }
  });
});

var _detector = require('./detector');

Object.keys(_detector).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _detector[key];
    }
  });
});

var _version = require('./version');

Object.keys(_version).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _version[key];
    }
  });
});

var _mobile = require('./mobile');

Object.keys(_mobile).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _mobile[key];
    }
  });
});

var _vr = require('./vr');

Object.keys(_vr).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _vr[key];
    }
  });
});

var _animation = require('./animation');

Object.keys(_animation).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _animation[key];
    }
  });
});

var _event = require('./event');

Object.keys(_event).forEach(function (key) {
  if (key === "default" || key === "__esModule") return;
  Object.defineProperty(exports, key, {
    enumerable: true,
    get: function get() {
      return _event[key];
    }
  });
});

},{"./animation":33,"./detector":34,"./event":35,"./merge-options":37,"./mobile":38,"./version":39,"./vr":40,"./warning":41}],37:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.isObject = isObject;
exports.isPlain = isPlain;


/**
 * code adopt from https://github.com/videojs/video.js/blob/master/src/js/utils/merge-options.js
 */

/**
 * Returns whether a value is an object of any kind - including DOM nodes,
 * arrays, regular expressions, etc. Not functions, though.
 *
 * This avoids the gotcha where using `typeof` on a `null` value
 * results in `'object'`.
 *
 * @param  {Object} value
 * @return {Boolean}
 */
function isObject(value) {
    return !!value && (typeof value === 'undefined' ? 'undefined' : _typeof(value)) === 'object';
}

/**
 * Returns whether an object appears to be a "plain" object - that is, a
 * direct instance of `Object`.
 *
 * @param  {Object} value
 * @return {Boolean}
 */
function isPlain(value) {
    return isObject(value) && Object.prototype.toString.call(value) === '[object Object]' && value.constructor === Object;
}

var mergeOptions = exports.mergeOptions = function mergeOptions() {
    for (var _len = arguments.length, sources = Array(_len), _key = 0; _key < _len; _key++) {
        sources[_key] = arguments[_key];
    }

    var results = {};
    sources.forEach(function (values) {
        if (!values) {
            return;
        }

        Object.getOwnPropertyNames(values).forEach(function (key) {
            var value = values[key];
            if (!isPlain(value)) {
                results[key] = value;
                return;
            }

            if (!isPlain(results[key])) {
                results[key] = {};
            }

            results[key] = mergeOptions(results[key], value);
        });
    });

    return results;
};

},{}],38:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.getTouchesDistance = getTouchesDistance;
exports.mobileAndTabletcheck = mobileAndTabletcheck;
exports.isIos = isIos;
exports.isRealIphone = isRealIphone;
function getTouchesDistance(touches) {
    return Math.sqrt((touches[0].clientX - touches[1].clientX) * (touches[0].clientX - touches[1].clientX) + (touches[0].clientY - touches[1].clientY) * (touches[0].clientY - touches[1].clientY));
}

function mobileAndTabletcheck() {
    var check = false;
    (function (a) {
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    return check;
}

function isIos() {
    return (/iPhone|iPad|iPod/i.test(navigator.userAgent)
    );
}

function isRealIphone() {
    return (/iPhone|iPod/i.test(navigator.platform)
    );
}

},{}],39:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.getVideojsVersion = getVideojsVersion;
function getVideojsVersion(str) {
    var index = str.indexOf(".");
    if (index === -1) return 0;
    var major = parseInt(str.substring(0, index));
    return major;
}

},{}],40:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.fovToProjection = fovToProjection;

var _three = (typeof window !== "undefined" ? window['THREE'] : typeof global !== "undefined" ? global['THREE'] : null);

var _three2 = _interopRequireDefault(_three);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

//adopt code from: https://github.com/MozVR/vr-web-examples/blob/master/threejs-vr-boilerplate/js/VREffect.js
function fovToNDCScaleOffset(fov) {
    var pxscale = 2.0 / (fov.leftTan + fov.rightTan);
    var pxoffset = (fov.leftTan - fov.rightTan) * pxscale * 0.5;
    var pyscale = 2.0 / (fov.upTan + fov.downTan);
    var pyoffset = (fov.upTan - fov.downTan) * pyscale * 0.5;
    return { scale: [pxscale, pyscale], offset: [pxoffset, pyoffset] };
}

function fovPortToProjection(fov, rightHanded, zNear, zFar) {

    rightHanded = rightHanded === undefined ? true : rightHanded;
    zNear = zNear === undefined ? 0.01 : zNear;
    zFar = zFar === undefined ? 10000.0 : zFar;

    var handednessScale = rightHanded ? -1.0 : 1.0;

    // start with an identity matrix
    var mobj = new _three2.default.Matrix4();
    var m = mobj.elements;

    // and with scale/offset info for normalized device coords
    var scaleAndOffset = fovToNDCScaleOffset(fov);

    // X result, map clip edges to [-w,+w]
    m[0 * 4 + 0] = scaleAndOffset.scale[0];
    m[0 * 4 + 1] = 0.0;
    m[0 * 4 + 2] = scaleAndOffset.offset[0] * handednessScale;
    m[0 * 4 + 3] = 0.0;

    // Y result, map clip edges to [-w,+w]
    // Y offset is negated because this proj matrix transforms from world coords with Y=up,
    // but the NDC scaling has Y=down (thanks D3D?)
    m[1 * 4 + 0] = 0.0;
    m[1 * 4 + 1] = scaleAndOffset.scale[1];
    m[1 * 4 + 2] = -scaleAndOffset.offset[1] * handednessScale;
    m[1 * 4 + 3] = 0.0;

    // Z result (up to the app)
    m[2 * 4 + 0] = 0.0;
    m[2 * 4 + 1] = 0.0;
    m[2 * 4 + 2] = zFar / (zNear - zFar) * -handednessScale;
    m[2 * 4 + 3] = zFar * zNear / (zNear - zFar);

    // W result (= Z in)
    m[3 * 4 + 0] = 0.0;
    m[3 * 4 + 1] = 0.0;
    m[3 * 4 + 2] = handednessScale;
    m[3 * 4 + 3] = 0.0;

    mobj.transpose();

    return mobj;
}

function fovToProjection(fov, rightHanded, zNear, zFar) {
    var DEG2RAD = Math.PI / 180.0;

    var fovPort = {
        upTan: Math.tan(fov.upDegrees * DEG2RAD),
        downTan: Math.tan(fov.downDegrees * DEG2RAD),
        leftTan: Math.tan(fov.leftDegrees * DEG2RAD),
        rightTan: Math.tan(fov.rightDegrees * DEG2RAD)
    };

    return fovPortToProjection(fovPort, rightHanded, zNear, zFar);
}

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{}],41:[function(require,module,exports){
(function (process){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});


/**
 * Prints a warning in the console if it exists.
 * Disable on production environment.
 *
 * @param {String} message The warning message.
 * @returns {void}
 */
var warning = exports.warning = function warning(message) {
    //warning message only happen on develop environment
    if (process.env.NODE_ENV !== 'production') {
        if (typeof console !== "undefined" && typeof console.error === "function") {
            console.error(message);
        }

        try {
            throw new Error(message);
        } catch (e) {}
    }
};

var crossDomainWarning = exports.crossDomainWarning = function crossDomainWarning() {
    var element = document.createElement('div');
    element.className = "vjs-cross-domain-unsupport";
    element.innerHTML = "Sorry, Your browser don't support cross domain.";
    return element;
};

}).call(this,require('_process'))

},{"_process":1}]},{},[26])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJub2RlX21vZHVsZXMvYnJvd3NlcmlmeS9ub2RlX21vZHVsZXMvcHJvY2Vzcy9icm93c2VyLmpzIiwibm9kZV9tb2R1bGVzL2ludGVydmFsb21ldGVyL2Rpc3QvaW50ZXJ2YWxvbWV0ZXIuY29tbW9uLWpzLmpzIiwibm9kZV9tb2R1bGVzL2lwaG9uZS1pbmxpbmUtdmlkZW8vZGlzdC9pcGhvbmUtaW5saW5lLXZpZGVvLmNvbW1vbi1qcy5qcyIsIm5vZGVfbW9kdWxlcy9wb29yLW1hbnMtc3ltYm9sL2Rpc3QvcG9vci1tYW5zLXN5bWJvbC5jb21tb24tanMuanMiLCJub2RlX21vZHVsZXMvd29sZnk4Ny1ldmVudGVtaXR0ZXIvRXZlbnRFbWl0dGVyLmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9BbmltYXRpb24uanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL0Jhc2VDYW52YXMuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL0J1dHRvbi5qcyIsInNyYy9zY3JpcHRzL0NvbXBvbmVudHMvQ2xpY2thYmxlQ29tcG9uZW50LmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9Db21wb25lbnQuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL0R1YWxGaXNoZXllLmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9FcXVpcmVjdGFuZ3VsYXIuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL0Zpc2hleWUuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL0hlbHBlckNhbnZhcy5qcyIsInNyYy9zY3JpcHRzL0NvbXBvbmVudHMvTWFya2VyLmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9NYXJrZXJDb250YWluZXIuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL01hcmtlckdyb3VwLmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9Ob3RpZmljYXRpb24uanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL1RocmVlRFZpZGVvLmpzIiwic3JjL3NjcmlwdHMvQ29tcG9uZW50cy9UaHVtYm5haWwuanMiLCJzcmMvc2NyaXB0cy9Db21wb25lbnRzL1R3b0RWaWRlby5qcyIsInNyYy9zY3JpcHRzL0NvbXBvbmVudHMvVlIxODAzRC5qcyIsInNyYy9zY3JpcHRzL0NvbXBvbmVudHMvVlIzNjAzRC5qcyIsInNyYy9zY3JpcHRzL0NvbXBvbmVudHMvVlJCdXR0b24uanMiLCJzcmMvc2NyaXB0cy9QYW5vcmFtYS5qcyIsInNyYy9zY3JpcHRzL2luZGV4LmpzIiwic3JjL3NjcmlwdHMvdGVjaC9CYXNlUGxheWVyLmpzIiwic3JjL3NjcmlwdHMvdGVjaC9Mb2FkZXIuanMiLCJzcmMvc2NyaXB0cy90ZWNoL01lZGlhRWxlbWVudFBsYXllci5qcyIsInNyYy9zY3JpcHRzL3RlY2gvVmlkZW9qczQuanMiLCJzcmMvc2NyaXB0cy90ZWNoL1ZpZGVvanM1LmpzIiwic3JjL3NjcmlwdHMvdGVjaC92aWRlb2pzLmpzIiwic3JjL3NjcmlwdHMvdXRpbHMvYW5pbWF0aW9uLmpzIiwic3JjL3NjcmlwdHMvdXRpbHMvZGV0ZWN0b3IuanMiLCJzcmMvc2NyaXB0cy91dGlscy9ldmVudC5qcyIsInNyYy9zY3JpcHRzL3V0aWxzL2luZGV4LmpzIiwic3JjL3NjcmlwdHMvdXRpbHMvbWVyZ2Utb3B0aW9ucy5qcyIsInNyYy9zY3JpcHRzL3V0aWxzL21vYmlsZS5qcyIsInNyYy9zY3JpcHRzL3V0aWxzL3ZlcnNpb24uanMiLCJzcmMvc2NyaXB0cy91dGlscy92ci5qcyIsInNyYy9zY3JpcHRzL3V0aWxzL3dhcm5pbmcuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNwTEE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ3pDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUN2VUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDTkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FB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LEVBQVUsQ0FDWDtBQUNKO0FBQ0osQ0FaTTs7QUFjQSxJQUFNLGtEQUFxQixTQUFyQixrQkFBcUIsR0FBbUI7QUFDakQsUUFBSSxVQUFVLFNBQVMsYUFBVCxDQUF3QixLQUF4QixDQUFkO0FBQ0EsWUFBUSxTQUFSLEdBQW9CLDRCQUFwQjtBQUNBLFlBQVEsU0FBUixHQUFvQixpREFBcEI7QUFDQSxXQUFPLE9BQVA7QUFDSCxDQUxNIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsIi8vIHNoaW0gZm9yIHVzaW5nIHByb2Nlc3MgaW4gYnJvd3NlclxudmFyIHByb2Nlc3MgPSBtb2R1bGUuZXhwb3J0cyA9IHt9O1xuXG4vLyBjYWNoZWQgZnJvbSB3aGF0ZXZlciBnbG9iYWwgaXMgcHJlc2VudCBzbyB0aGF0IHRlc3QgcnVubmVycyB0aGF0IHN0dWIgaXRcbi8vIGRvbid0IGJyZWFrIHRoaW5ncy4gIEJ1dCB3ZSBuZWVkIHRvIHdyYXAgaXQgaW4gYSB0cnkgY2F0Y2ggaW4gY2FzZSBpdCBpc1xuLy8gd3JhcHBlZCBpbiBzdHJpY3QgbW9kZSBjb2RlIHdoaWNoIGRvZXNuJ3QgZGVmaW5lIGFueSBnbG9iYWxzLiAgSXQncyBpbnNpZGUgYVxuLy8gZnVuY3Rpb24gYmVjYXVzZSB0cnkvY2F0Y2hlcyBkZW9wdGltaXplIGluIGNlcnRhaW4gZW5naW5lcy5cblxudmFyIGNhY2hlZFNldFRpbWVvdXQ7XG52YXIgY2FjaGVkQ2xlYXJUaW1lb3V0O1xuXG5mdW5jdGlvbiBkZWZhdWx0U2V0VGltb3V0KCkge1xuICAgIHRocm93IG5ldyBFcnJvcignc2V0VGltZW91dCBoYXMgbm90IGJlZW4gZGVmaW5lZCcpO1xufVxuZnVuY3Rpb24gZGVmYXVsdENsZWFyVGltZW91dCAoKSB7XG4gICAgdGhyb3cgbmV3IEVycm9yKCdjbGVhclRpbWVvdXQgaGFzIG5vdCBiZWVuIGRlZmluZWQnKTtcbn1cbihmdW5jdGlvbiAoKSB7XG4gICAgdHJ5IHtcbiAgICAgICAgaWYgKHR5cGVvZiBzZXRUaW1lb3V0ID09PSAnZnVuY3Rpb24nKSB7XG4gICAgICAgICAgICBjYWNoZWRTZXRUaW1lb3V0ID0gc2V0VGltZW91dDtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIGNhY2hlZFNldFRpbWVvdXQgPSBkZWZhdWx0U2V0VGltb3V0O1xuICAgICAgICB9XG4gICAgfSBjYXRjaCAoZSkge1xuICAgICAgICBjYWNoZWRTZXRUaW1lb3V0ID0gZGVmYXVsdFNldFRpbW91dDtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgICAgaWYgKHR5cGVvZiBjbGVhclRpbWVvdXQgPT09ICdmdW5jdGlvbicpIHtcbiAgICAgICAgICAgIGNhY2hlZENsZWFyVGltZW91dCA9IGNsZWFyVGltZW91dDtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIGNhY2hlZENsZWFyVGltZW91dCA9IGRlZmF1bHRDbGVhclRpbWVvdXQ7XG4gICAgICAgIH1cbiAgICB9IGNhdGNoIChlKSB7XG4gICAgICAgIGNhY2hlZENsZWFyVGltZW91dCA9IGRlZmF1bHRDbGVhclRpbWVvdXQ7XG4gICAgfVxufSAoKSlcbmZ1bmN0aW9uIHJ1blRpbWVvdXQoZnVuKSB7XG4gICAgaWYgKGNhY2hlZFNldFRpbWVvdXQgPT09IHNldFRpbWVvdXQpIHtcbiAgICAgICAgLy9ub3JtYWwgZW52aXJvbWVudHMgaW4gc2FuZSBzaXR1YXRpb25zXG4gICAgICAgIHJldHVybiBzZXRUaW1lb3V0KGZ1biwgMCk7XG4gICAgfVxuICAgIC8vIGlmIHNldFRpbWVvdXQgd2Fzbid0IGF2YWlsYWJsZSBidXQgd2FzIGxhdHRlciBkZWZpbmVkXG4gICAgaWYgKChjYWNoZWRTZXRUaW1lb3V0ID09PSBkZWZhdWx0U2V0VGltb3V0IHx8ICFjYWNoZWRTZXRUaW1lb3V0KSAmJiBzZXRUaW1lb3V0KSB7XG4gICAgICAgIGNhY2hlZFNldFRpbWVvdXQgPSBzZXRUaW1lb3V0O1xuICAgICAgICByZXR1cm4gc2V0VGltZW91dChmdW4sIDApO1xuICAgIH1cbiAgICB0cnkge1xuICAgICAgICAvLyB3aGVuIHdoZW4gc29tZWJvZHkgaGFzIHNjcmV3ZWQgd2l0aCBzZXRUaW1lb3V0IGJ1dCBubyBJLkUuIG1hZGRuZXNzXG4gICAgICAgIHJldHVybiBjYWNoZWRTZXRUaW1lb3V0KGZ1biwgMCk7XG4gICAgfSBjYXRjaChlKXtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIC8vIFdoZW4gd2UgYXJlIGluIEkuRS4gYnV0IHRoZSBzY3JpcHQgaGFzIGJlZW4gZXZhbGVkIHNvIEkuRS4gZG9lc24ndCB0cnVzdCB0aGUgZ2xvYmFsIG9iamVjdCB3aGVuIGNhbGxlZCBub3JtYWxseVxuICAgICAgICAgICAgcmV0dXJuIGNhY2hlZFNldFRpbWVvdXQuY2FsbChudWxsLCBmdW4sIDApO1xuICAgICAgICB9IGNhdGNoKGUpe1xuICAgICAgICAgICAgLy8gc2FtZSBhcyBhYm92ZSBidXQgd2hlbiBpdCdzIGEgdmVyc2lvbiBvZiBJLkUuIHRoYXQgbXVzdCBoYXZlIHRoZSBnbG9iYWwgb2JqZWN0IGZvciAndGhpcycsIGhvcGZ1bGx5IG91ciBjb250ZXh0IGNvcnJlY3Qgb3RoZXJ3aXNlIGl0IHdpbGwgdGhyb3cgYSBnbG9iYWwgZXJyb3JcbiAgICAgICAgICAgIHJldHVybiBjYWNoZWRTZXRUaW1lb3V0LmNhbGwodGhpcywgZnVuLCAwKTtcbiAgICAgICAgfVxuICAgIH1cblxuXG59XG5mdW5jdGlvbiBydW5DbGVhclRpbWVvdXQobWFya2VyKSB7XG4gICAgaWYgKGNhY2hlZENsZWFyVGltZW91dCA9PT0gY2xlYXJUaW1lb3V0KSB7XG4gICAgICAgIC8vbm9ybWFsIGVudmlyb21lbnRzIGluIHNhbmUgc2l0dWF0aW9uc1xuICAgICAgICByZXR1cm4gY2xlYXJUaW1lb3V0KG1hcmtlcik7XG4gICAgfVxuICAgIC8vIGlmIGNsZWFyVGltZW91dCB3YXNuJ3QgYXZhaWxhYmxlIGJ1dCB3YXMgbGF0dGVyIGRlZmluZWRcbiAgICBpZiAoKGNhY2hlZENsZWFyVGltZW91dCA9PT0gZGVmYXVsdENsZWFyVGltZW91dCB8fCAhY2FjaGVkQ2xlYXJUaW1lb3V0KSAmJiBjbGVhclRpbWVvdXQpIHtcbiAgICAgICAgY2FjaGVkQ2xlYXJUaW1lb3V0ID0gY2xlYXJUaW1lb3V0O1xuICAgICAgICByZXR1cm4gY2xlYXJUaW1lb3V0KG1hcmtlcik7XG4gICAgfVxuICAgIHRyeSB7XG4gICAgICAgIC8vIHdoZW4gd2hlbiBzb21lYm9keSBoYXMgc2NyZXdlZCB3aXRoIHNldFRpbWVvdXQgYnV0IG5vIEkuRS4gbWFkZG5lc3NcbiAgICAgICAgcmV0dXJuIGNhY2hlZENsZWFyVGltZW91dChtYXJrZXIpO1xuICAgIH0gY2F0Y2ggKGUpe1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgLy8gV2hlbiB3ZSBhcmUgaW4gSS5FLiBidXQgdGhlIHNjcmlwdCBoYXMgYmVlbiBldmFsZWQgc28gSS5FLiBkb2Vzbid0ICB0cnVzdCB0aGUgZ2xvYmFsIG9iamVjdCB3aGVuIGNhbGxlZCBub3JtYWxseVxuICAgICAgICAgICAgcmV0dXJuIGNhY2hlZENsZWFyVGltZW91dC5jYWxsKG51bGwsIG1hcmtlcik7XG4gICAgICAgIH0gY2F0Y2ggKGUpe1xuICAgICAgICAgICAgLy8gc2FtZSBhcyBhYm92ZSBidXQgd2hlbiBpdCdzIGEgdmVyc2lvbiBvZiBJLkUuIHRoYXQgbXVzdCBoYXZlIHRoZSBnbG9iYWwgb2JqZWN0IGZvciAndGhpcycsIGhvcGZ1bGx5IG91ciBjb250ZXh0IGNvcnJlY3Qgb3RoZXJ3aXNlIGl0IHdpbGwgdGhyb3cgYSBnbG9iYWwgZXJyb3IuXG4gICAgICAgICAgICAvLyBTb21lIHZlcnNpb25zIG9mIEkuRS4gaGF2ZSBkaWZmZXJlbnQgcnVsZXMgZm9yIGNsZWFyVGltZW91dCB2cyBzZXRUaW1lb3V0XG4gICAgICAgICAgICByZXR1cm4gY2FjaGVkQ2xlYXJUaW1lb3V0LmNhbGwodGhpcywgbWFya2VyKTtcbiAgICAgICAgfVxuICAgIH1cblxuXG5cbn1cbnZhciBxdWV1ZSA9IFtdO1xudmFyIGRyYWluaW5nID0gZmFsc2U7XG52YXIgY3VycmVudFF1ZXVlO1xudmFyIHF1ZXVlSW5kZXggPSAtMTtcblxuZnVuY3Rpb24gY2xlYW5VcE5leHRUaWNrKCkge1xuICAgIGlmICghZHJhaW5pbmcgfHwgIWN1cnJlbnRRdWV1ZSkge1xuICAgICAgICByZXR1cm47XG4gICAgfVxuICAgIGRyYWluaW5nID0gZmFsc2U7XG4gICAgaWYgKGN1cnJlbnRRdWV1ZS5sZW5ndGgpIHtcbiAgICAgICAgcXVldWUgPSBjdXJyZW50UXVldWUuY29uY2F0KHF1ZXVlKTtcbiAgICB9IGVsc2Uge1xuICAgICAgICBxdWV1ZUluZGV4ID0gLTE7XG4gICAgfVxuICAgIGlmIChxdWV1ZS5sZW5ndGgpIHtcbiAgICAgICAgZHJhaW5RdWV1ZSgpO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gZHJhaW5RdWV1ZSgpIHtcbiAgICBpZiAoZHJhaW5pbmcpIHtcbiAgICAgICAgcmV0dXJuO1xuICAgIH1cbiAgICB2YXIgdGltZW91dCA9IHJ1blRpbWVvdXQoY2xlYW5VcE5leHRUaWNrKTtcbiAgICBkcmFpbmluZyA9IHRydWU7XG5cbiAgICB2YXIgbGVuID0gcXVldWUubGVuZ3RoO1xuICAgIHdoaWxlKGxlbikge1xuICAgICAgICBjdXJyZW50UXVldWUgPSBxdWV1ZTtcbiAgICAgICAgcXVldWUgPSBbXTtcbiAgICAgICAgd2hpbGUgKCsrcXVldWVJbmRleCA8IGxlbikge1xuICAgICAgICAgICAgaWYgKGN1cnJlbnRRdWV1ZSkge1xuICAgICAgICAgICAgICAgIGN1cnJlbnRRdWV1ZVtxdWV1ZUluZGV4XS5ydW4oKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBxdWV1ZUluZGV4ID0gLTE7XG4gICAgICAgIGxlbiA9IHF1ZXVlLmxlbmd0aDtcbiAgICB9XG4gICAgY3VycmVudFF1ZXVlID0gbnVsbDtcbiAgICBkcmFpbmluZyA9IGZhbHNlO1xuICAgIHJ1bkNsZWFyVGltZW91dCh0aW1lb3V0KTtcbn1cblxucHJvY2Vzcy5uZXh0VGljayA9IGZ1bmN0aW9uIChmdW4pIHtcbiAgICB2YXIgYXJncyA9IG5ldyBBcnJheShhcmd1bWVudHMubGVuZ3RoIC0gMSk7XG4gICAgaWYgKGFyZ3VtZW50cy5sZW5ndGggPiAxKSB7XG4gICAgICAgIGZvciAodmFyIGkgPSAxOyBpIDwgYXJndW1lbnRzLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgICAgICBhcmdzW2kgLSAxXSA9IGFyZ3VtZW50c1tpXTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBxdWV1ZS5wdXNoKG5ldyBJdGVtKGZ1biwgYXJncykpO1xuICAgIGlmIChxdWV1ZS5sZW5ndGggPT09IDEgJiYgIWRyYWluaW5nKSB7XG4gICAgICAgIHJ1blRpbWVvdXQoZHJhaW5RdWV1ZSk7XG4gICAgfVxufTtcblxuLy8gdjggbGlrZXMgcHJlZGljdGlibGUgb2JqZWN0c1xuZnVuY3Rpb24gSXRlbShmdW4sIGFycmF5KSB7XG4gICAgdGhpcy5mdW4gPSBmdW47XG4gICAgdGhpcy5hcnJheSA9IGFycmF5O1xufVxuSXRlbS5wcm90b3R5cGUucnVuID0gZnVuY3Rpb24gKCkge1xuICAgIHRoaXMuZnVuLmFwcGx5KG51bGwsIHRoaXMuYXJyYXkpO1xufTtcbnByb2Nlc3MudGl0bGUgPSAnYnJvd3Nlcic7XG5wcm9jZXNzLmJyb3dzZXIgPSB0cnVlO1xucHJvY2Vzcy5lbnYgPSB7fTtcbnByb2Nlc3MuYXJndiA9IFtdO1xucHJvY2Vzcy52ZXJzaW9uID0gJyc7IC8vIGVtcHR5IHN0cmluZyB0byBhdm9pZCByZWdleHAgaXNzdWVzXG5wcm9jZXNzLnZlcnNpb25zID0ge307XG5cbmZ1bmN0aW9uIG5vb3AoKSB7fVxuXG5wcm9jZXNzLm9uID0gbm9vcDtcbnByb2Nlc3MuYWRkTGlzdGVuZXIgPSBub29wO1xucHJvY2Vzcy5vbmNlID0gbm9vcDtcbnByb2Nlc3Mub2ZmID0gbm9vcDtcbnByb2Nlc3MucmVtb3ZlTGlzdGVuZXIgPSBub29wO1xucHJvY2Vzcy5yZW1vdmVBbGxMaXN0ZW5lcnMgPSBub29wO1xucHJvY2Vzcy5lbWl0ID0gbm9vcDtcblxucHJvY2Vzcy5iaW5kaW5nID0gZnVuY3Rpb24gKG5hbWUpIHtcbiAgICB0aHJvdyBuZXcgRXJyb3IoJ3Byb2Nlc3MuYmluZGluZyBpcyBub3Qgc3VwcG9ydGVkJyk7XG59O1xuXG5wcm9jZXNzLmN3ZCA9IGZ1bmN0aW9uICgpIHsgcmV0dXJuICcvJyB9O1xucHJvY2Vzcy5jaGRpciA9IGZ1bmN0aW9uIChkaXIpIHtcbiAgICB0aHJvdyBuZXcgRXJyb3IoJ3Byb2Nlc3MuY2hkaXIgaXMgbm90IHN1cHBvcnRlZCcpO1xufTtcbnByb2Nlc3MudW1hc2sgPSBmdW5jdGlvbigpIHsgcmV0dXJuIDA7IH07XG4iLCIvKiEgbnBtLmltL2ludGVydmFsb21ldGVyICovXG4ndXNlIHN0cmljdCc7XG5cbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCAnX19lc01vZHVsZScsIHsgdmFsdWU6IHRydWUgfSk7XG5cbmZ1bmN0aW9uIGludGVydmFsb21ldGVyKGNiLCByZXF1ZXN0LCBjYW5jZWwsIHJlcXVlc3RQYXJhbWV0ZXIpIHtcblx0dmFyIHJlcXVlc3RJZDtcblx0dmFyIHByZXZpb3VzTG9vcFRpbWU7XG5cdGZ1bmN0aW9uIGxvb3Aobm93KSB7XG5cdFx0Ly8gbXVzdCBiZSByZXF1ZXN0ZWQgYmVmb3JlIGNiKCkgYmVjYXVzZSB0aGF0IG1pZ2h0IGNhbGwgLnN0b3AoKVxuXHRcdHJlcXVlc3RJZCA9IHJlcXVlc3QobG9vcCwgcmVxdWVzdFBhcmFtZXRlcik7XG5cblx0XHQvLyBjYWxsZWQgd2l0aCBcIm1zIHNpbmNlIGxhc3QgY2FsbFwiLiAwIG9uIHN0YXJ0KClcblx0XHRjYihub3cgLSAocHJldmlvdXNMb29wVGltZSB8fCBub3cpKTtcblxuXHRcdHByZXZpb3VzTG9vcFRpbWUgPSBub3c7XG5cdH1cblx0cmV0dXJuIHtcblx0XHRzdGFydDogZnVuY3Rpb24gc3RhcnQoKSB7XG5cdFx0XHRpZiAoIXJlcXVlc3RJZCkgeyAvLyBwcmV2ZW50IGRvdWJsZSBzdGFydHNcblx0XHRcdFx0bG9vcCgwKTtcblx0XHRcdH1cblx0XHR9LFxuXHRcdHN0b3A6IGZ1bmN0aW9uIHN0b3AoKSB7XG5cdFx0XHRjYW5jZWwocmVxdWVzdElkKTtcblx0XHRcdHJlcXVlc3RJZCA9IG51bGw7XG5cdFx0XHRwcmV2aW91c0xvb3BUaW1lID0gMDtcblx0XHR9XG5cdH07XG59XG5cbmZ1bmN0aW9uIGZyYW1lSW50ZXJ2YWxvbWV0ZXIoY2IpIHtcblx0cmV0dXJuIGludGVydmFsb21ldGVyKGNiLCByZXF1ZXN0QW5pbWF0aW9uRnJhbWUsIGNhbmNlbEFuaW1hdGlvbkZyYW1lKTtcbn1cblxuZnVuY3Rpb24gdGltZXJJbnRlcnZhbG9tZXRlcihjYiwgZGVsYXkpIHtcblx0cmV0dXJuIGludGVydmFsb21ldGVyKGNiLCBzZXRUaW1lb3V0LCBjbGVhclRpbWVvdXQsIGRlbGF5KTtcbn1cblxuZXhwb3J0cy5pbnRlcnZhbG9tZXRlciA9IGludGVydmFsb21ldGVyO1xuZXhwb3J0cy5mcmFtZUludGVydmFsb21ldGVyID0gZnJhbWVJbnRlcnZhbG9tZXRlcjtcbmV4cG9ydHMudGltZXJJbnRlcnZhbG9tZXRlciA9IHRpbWVySW50ZXJ2YWxvbWV0ZXI7IiwiLyohIG5wbS5pbS9pcGhvbmUtaW5saW5lLXZpZGVvICovXG4ndXNlIHN0cmljdCc7XG5cbmZ1bmN0aW9uIF9pbnRlcm9wRGVmYXVsdCAoZXgpIHsgcmV0dXJuIChleCAmJiAodHlwZW9mIGV4ID09PSAnb2JqZWN0JykgJiYgJ2RlZmF1bHQnIGluIGV4KSA/IGV4WydkZWZhdWx0J10gOiBleDsgfVxuXG52YXIgU3ltYm9sID0gX2ludGVyb3BEZWZhdWx0KHJlcXVpcmUoJ3Bvb3ItbWFucy1zeW1ib2wnKSk7XG52YXIgaW50ZXJ2YWxvbWV0ZXIgPSByZXF1aXJlKCdpbnRlcnZhbG9tZXRlcicpO1xuXG5mdW5jdGlvbiBwcmV2ZW50RXZlbnQoZWxlbWVudCwgZXZlbnROYW1lLCB0b2dnbGVQcm9wZXJ0eSwgcHJldmVudFdpdGhQcm9wZXJ0eSkge1xuXHRmdW5jdGlvbiBoYW5kbGVyKGUpIHtcblx0XHRpZiAoQm9vbGVhbihlbGVtZW50W3RvZ2dsZVByb3BlcnR5XSkgPT09IEJvb2xlYW4ocHJldmVudFdpdGhQcm9wZXJ0eSkpIHtcblx0XHRcdGUuc3RvcEltbWVkaWF0ZVByb3BhZ2F0aW9uKCk7XG5cdFx0XHQvLyBjb25zb2xlLmxvZyhldmVudE5hbWUsICdwcmV2ZW50ZWQgb24nLCBlbGVtZW50KTtcblx0XHR9XG5cdFx0ZGVsZXRlIGVsZW1lbnRbdG9nZ2xlUHJvcGVydHldO1xuXHR9XG5cdGVsZW1lbnQuYWRkRXZlbnRMaXN0ZW5lcihldmVudE5hbWUsIGhhbmRsZXIsIGZhbHNlKTtcblxuXHQvLyBSZXR1cm4gaGFuZGxlciB0byBhbGxvdyB0byBkaXNhYmxlIHRoZSBwcmV2ZW50aW9uLiBVc2FnZTpcblx0Ly8gY29uc3QgcHJldmVudGlvbkhhbmRsZXIgPSBwcmV2ZW50RXZlbnQoZWwsICdjbGljaycpO1xuXHQvLyBlbC5yZW1vdmVFdmVudEhhbmRsZXIoJ2NsaWNrJywgcHJldmVudGlvbkhhbmRsZXIpO1xuXHRyZXR1cm4gaGFuZGxlcjtcbn1cblxuZnVuY3Rpb24gcHJveHlQcm9wZXJ0eShvYmplY3QsIHByb3BlcnR5TmFtZSwgc291cmNlT2JqZWN0LCBjb3B5Rmlyc3QpIHtcblx0ZnVuY3Rpb24gZ2V0KCkge1xuXHRcdHJldHVybiBzb3VyY2VPYmplY3RbcHJvcGVydHlOYW1lXTtcblx0fVxuXHRmdW5jdGlvbiBzZXQodmFsdWUpIHtcblx0XHRzb3VyY2VPYmplY3RbcHJvcGVydHlOYW1lXSA9IHZhbHVlO1xuXHR9XG5cblx0aWYgKGNvcHlGaXJzdCkge1xuXHRcdHNldChvYmplY3RbcHJvcGVydHlOYW1lXSk7XG5cdH1cblxuXHRPYmplY3QuZGVmaW5lUHJvcGVydHkob2JqZWN0LCBwcm9wZXJ0eU5hbWUsIHtnZXQ6IGdldCwgc2V0OiBzZXR9KTtcbn1cblxuZnVuY3Rpb24gcHJveHlFdmVudChvYmplY3QsIGV2ZW50TmFtZSwgc291cmNlT2JqZWN0KSB7XG5cdHNvdXJjZU9iamVjdC5hZGRFdmVudExpc3RlbmVyKGV2ZW50TmFtZSwgZnVuY3Rpb24gKCkgeyByZXR1cm4gb2JqZWN0LmRpc3BhdGNoRXZlbnQobmV3IEV2ZW50KGV2ZW50TmFtZSkpOyB9KTtcbn1cblxuZnVuY3Rpb24gZGlzcGF0Y2hFdmVudEFzeW5jKGVsZW1lbnQsIHR5cGUpIHtcblx0UHJvbWlzZS5yZXNvbHZlKCkudGhlbihmdW5jdGlvbiAoKSB7XG5cdFx0ZWxlbWVudC5kaXNwYXRjaEV2ZW50KG5ldyBFdmVudCh0eXBlKSk7XG5cdH0pO1xufVxuXG4vLyBpT1MgMTAgYWRkcyBzdXBwb3J0IGZvciBuYXRpdmUgaW5saW5lIHBsYXliYWNrICsgc2lsZW50IGF1dG9wbGF5XG52YXIgaXNXaGl0ZWxpc3RlZCA9IC9pUGhvbmV8aVBvZC9pLnRlc3QobmF2aWdhdG9yLnVzZXJBZ2VudCkgJiYgIW1hdGNoTWVkaWEoJygtd2Via2l0LXZpZGVvLXBsYXlhYmxlLWlubGluZSknKS5tYXRjaGVzO1xuXG52YXIg4LKgID0gU3ltYm9sKCk7XG52YXIg4LKgZXZlbnQgPSBTeW1ib2woKTtcbnZhciDgsqBwbGF5ID0gU3ltYm9sKCduYXRpdmVwbGF5Jyk7XG52YXIg4LKgcGF1c2UgPSBTeW1ib2woJ25hdGl2ZXBhdXNlJyk7XG5cbi8qKlxuICogVVRJTFNcbiAqL1xuXG5mdW5jdGlvbiBnZXRBdWRpb0Zyb21WaWRlbyh2aWRlbykge1xuXHR2YXIgYXVkaW8gPSBuZXcgQXVkaW8oKTtcblx0cHJveHlFdmVudCh2aWRlbywgJ3BsYXknLCBhdWRpbyk7XG5cdHByb3h5RXZlbnQodmlkZW8sICdwbGF5aW5nJywgYXVkaW8pO1xuXHRwcm94eUV2ZW50KHZpZGVvLCAncGF1c2UnLCBhdWRpbyk7XG5cdGF1ZGlvLmNyb3NzT3JpZ2luID0gdmlkZW8uY3Jvc3NPcmlnaW47XG5cblx0Ly8gJ2RhdGE6JyBjYXVzZXMgYXVkaW8ubmV0d29ya1N0YXRlID4gMFxuXHQvLyB3aGljaCB0aGVuIGFsbG93cyB0byBrZWVwIDxhdWRpbz4gaW4gYSByZXN1bWFibGUgcGxheWluZyBzdGF0ZVxuXHQvLyBpLmUuIG9uY2UgeW91IHNldCBhIHJlYWwgc3JjIGl0IHdpbGwga2VlcCBwbGF5aW5nIGlmIGl0IHdhcyBpZiAucGxheSgpIHdhcyBjYWxsZWRcblx0YXVkaW8uc3JjID0gdmlkZW8uc3JjIHx8IHZpZGVvLmN1cnJlbnRTcmMgfHwgJ2RhdGE6JztcblxuXHQvLyBpZiAoYXVkaW8uc3JjID09PSAnZGF0YTonKSB7XG5cdC8vICAgVE9ETzogd2FpdCBmb3IgdmlkZW8gdG8gYmUgc2VsZWN0ZWRcblx0Ly8gfVxuXHRyZXR1cm4gYXVkaW87XG59XG5cbnZhciBsYXN0UmVxdWVzdHMgPSBbXTtcbnZhciByZXF1ZXN0SW5kZXggPSAwO1xudmFyIGxhc3RUaW1ldXBkYXRlRXZlbnQ7XG5cbmZ1bmN0aW9uIHNldFRpbWUodmlkZW8sIHRpbWUsIHJlbWVtYmVyT25seSkge1xuXHQvLyBhbGxvdyBvbmUgdGltZXVwZGF0ZSBldmVudCBldmVyeSAyMDArIG1zXG5cdGlmICgobGFzdFRpbWV1cGRhdGVFdmVudCB8fCAwKSArIDIwMCA8IERhdGUubm93KCkpIHtcblx0XHR2aWRlb1vgsqBldmVudF0gPSB0cnVlO1xuXHRcdGxhc3RUaW1ldXBkYXRlRXZlbnQgPSBEYXRlLm5vdygpO1xuXHR9XG5cdGlmICghcmVtZW1iZXJPbmx5KSB7XG5cdFx0dmlkZW8uY3VycmVudFRpbWUgPSB0aW1lO1xuXHR9XG5cdGxhc3RSZXF1ZXN0c1srK3JlcXVlc3RJbmRleCAlIDNdID0gdGltZSAqIDEwMCB8IDAgLyAxMDA7XG59XG5cbmZ1bmN0aW9uIGlzUGxheWVyRW5kZWQocGxheWVyKSB7XG5cdHJldHVybiBwbGF5ZXIuZHJpdmVyLmN1cnJlbnRUaW1lID49IHBsYXllci52aWRlby5kdXJhdGlvbjtcbn1cblxuZnVuY3Rpb24gdXBkYXRlKHRpbWVEaWZmKSB7XG5cdHZhciBwbGF5ZXIgPSB0aGlzO1xuXHQvLyBjb25zb2xlLmxvZygndXBkYXRlJywgcGxheWVyLnZpZGVvLnJlYWR5U3RhdGUsIHBsYXllci52aWRlby5uZXR3b3JrU3RhdGUsIHBsYXllci5kcml2ZXIucmVhZHlTdGF0ZSwgcGxheWVyLmRyaXZlci5uZXR3b3JrU3RhdGUsIHBsYXllci5kcml2ZXIucGF1c2VkKTtcblx0aWYgKHBsYXllci52aWRlby5yZWFkeVN0YXRlID49IHBsYXllci52aWRlby5IQVZFX0ZVVFVSRV9EQVRBKSB7XG5cdFx0aWYgKCFwbGF5ZXIuaGFzQXVkaW8pIHtcblx0XHRcdHBsYXllci5kcml2ZXIuY3VycmVudFRpbWUgPSBwbGF5ZXIudmlkZW8uY3VycmVudFRpbWUgKyAoKHRpbWVEaWZmICogcGxheWVyLnZpZGVvLnBsYXliYWNrUmF0ZSkgLyAxMDAwKTtcblx0XHRcdGlmIChwbGF5ZXIudmlkZW8ubG9vcCAmJiBpc1BsYXllckVuZGVkKHBsYXllcikpIHtcblx0XHRcdFx0cGxheWVyLmRyaXZlci5jdXJyZW50VGltZSA9IDA7XG5cdFx0XHR9XG5cdFx0fVxuXHRcdHNldFRpbWUocGxheWVyLnZpZGVvLCBwbGF5ZXIuZHJpdmVyLmN1cnJlbnRUaW1lKTtcblx0fSBlbHNlIGlmIChwbGF5ZXIudmlkZW8ubmV0d29ya1N0YXRlID09PSBwbGF5ZXIudmlkZW8uTkVUV09SS19JRExFICYmICFwbGF5ZXIudmlkZW8uYnVmZmVyZWQubGVuZ3RoKSB7XG5cdFx0Ly8gdGhpcyBzaG91bGQgaGFwcGVuIHdoZW4gdGhlIHNvdXJjZSBpcyBhdmFpbGFibGUgYnV0OlxuXHRcdC8vIC0gaXQncyBwb3RlbnRpYWxseSBwbGF5aW5nICgucGF1c2VkID09PSBmYWxzZSlcblx0XHQvLyAtIGl0J3Mgbm90IHJlYWR5IHRvIHBsYXlcblx0XHQvLyAtIGl0J3Mgbm90IGxvYWRpbmdcblx0XHQvLyBJZiBpdCBoYXNBdWRpbywgdGhhdCB3aWxsIGJlIGxvYWRlZCBpbiB0aGUgJ2VtcHRpZWQnIGhhbmRsZXIgYmVsb3dcblx0XHRwbGF5ZXIudmlkZW8ubG9hZCgpO1xuXHRcdC8vIGNvbnNvbGUubG9nKCdXaWxsIGxvYWQnKTtcblx0fVxuXG5cdC8vIGNvbnNvbGUuYXNzZXJ0KHBsYXllci52aWRlby5jdXJyZW50VGltZSA9PT0gcGxheWVyLmRyaXZlci5jdXJyZW50VGltZSwgJ1ZpZGVvIG5vdCB1cGRhdGluZyEnKTtcblxuXHRpZiAocGxheWVyLnZpZGVvLmVuZGVkKSB7XG5cdFx0ZGVsZXRlIHBsYXllci52aWRlb1vgsqBldmVudF07IC8vIGFsbG93IHRpbWV1cGRhdGUgZXZlbnRcblx0XHRwbGF5ZXIudmlkZW8ucGF1c2UodHJ1ZSk7XG5cdH1cbn1cblxuLyoqXG4gKiBNRVRIT0RTXG4gKi9cblxuZnVuY3Rpb24gcGxheSgpIHtcblx0Ly8gY29uc29sZS5sb2coJ3BsYXknKTtcblx0dmFyIHZpZGVvID0gdGhpcztcblx0dmFyIHBsYXllciA9IHZpZGVvW+CyoF07XG5cblx0Ly8gaWYgaXQncyBmdWxsc2NyZWVuLCB1c2UgdGhlIG5hdGl2ZSBwbGF5ZXJcblx0aWYgKHZpZGVvLndlYmtpdERpc3BsYXlpbmdGdWxsc2NyZWVuKSB7XG5cdFx0dmlkZW9b4LKgcGxheV0oKTtcblx0XHRyZXR1cm47XG5cdH1cblxuXHRpZiAocGxheWVyLmRyaXZlci5zcmMgIT09ICdkYXRhOicgJiYgcGxheWVyLmRyaXZlci5zcmMgIT09IHZpZGVvLnNyYykge1xuXHRcdC8vIGNvbnNvbGUubG9nKCdzcmMgY2hhbmdlZCBvbiBwbGF5JywgdmlkZW8uc3JjKTtcblx0XHRzZXRUaW1lKHZpZGVvLCAwLCB0cnVlKTtcblx0XHRwbGF5ZXIuZHJpdmVyLnNyYyA9IHZpZGVvLnNyYztcblx0fVxuXG5cdGlmICghdmlkZW8ucGF1c2VkKSB7XG5cdFx0cmV0dXJuO1xuXHR9XG5cdHBsYXllci5wYXVzZWQgPSBmYWxzZTtcblxuXHRpZiAoIXZpZGVvLmJ1ZmZlcmVkLmxlbmd0aCkge1xuXHRcdC8vIC5sb2FkKCkgY2F1c2VzIHRoZSBlbXB0aWVkIGV2ZW50XG5cdFx0Ly8gdGhlIGFsdGVybmF0aXZlIGlzIC5wbGF5KCkrLnBhdXNlKCkgYnV0IHRoYXQgdHJpZ2dlcnMgcGxheS9wYXVzZSBldmVudHMsIGV2ZW4gd29yc2Vcblx0XHQvLyBwb3NzaWJseSB0aGUgYWx0ZXJuYXRpdmUgaXMgcHJldmVudGluZyB0aGlzIGV2ZW50IG9ubHkgb25jZVxuXHRcdHZpZGVvLmxvYWQoKTtcblx0fVxuXG5cdHBsYXllci5kcml2ZXIucGxheSgpO1xuXHRwbGF5ZXIudXBkYXRlci5zdGFydCgpO1xuXG5cdGlmICghcGxheWVyLmhhc0F1ZGlvKSB7XG5cdFx0ZGlzcGF0Y2hFdmVudEFzeW5jKHZpZGVvLCAncGxheScpO1xuXHRcdGlmIChwbGF5ZXIudmlkZW8ucmVhZHlTdGF0ZSA+PSBwbGF5ZXIudmlkZW8uSEFWRV9FTk9VR0hfREFUQSkge1xuXHRcdFx0Ly8gY29uc29sZS5sb2coJ29ucGxheScpO1xuXHRcdFx0ZGlzcGF0Y2hFdmVudEFzeW5jKHZpZGVvLCAncGxheWluZycpO1xuXHRcdH1cblx0fVxufVxuZnVuY3Rpb24gcGF1c2UoZm9yY2VFdmVudHMpIHtcblx0Ly8gY29uc29sZS5sb2coJ3BhdXNlJyk7XG5cdHZhciB2aWRlbyA9IHRoaXM7XG5cdHZhciBwbGF5ZXIgPSB2aWRlb1vgsqBdO1xuXG5cdHBsYXllci5kcml2ZXIucGF1c2UoKTtcblx0cGxheWVyLnVwZGF0ZXIuc3RvcCgpO1xuXG5cdC8vIGlmIGl0J3MgZnVsbHNjcmVlbiwgdGhlIGRldmVsb3BlciB0aGUgbmF0aXZlIHBsYXllci5wYXVzZSgpXG5cdC8vIFRoaXMgaXMgYXQgdGhlIGVuZCBvZiBwYXVzZSgpIGJlY2F1c2UgaXQgYWxzb1xuXHQvLyBuZWVkcyB0byBtYWtlIHN1cmUgdGhhdCB0aGUgc2ltdWxhdGlvbiBpcyBwYXVzZWRcblx0aWYgKHZpZGVvLndlYmtpdERpc3BsYXlpbmdGdWxsc2NyZWVuKSB7XG5cdFx0dmlkZW9b4LKgcGF1c2VdKCk7XG5cdH1cblxuXHRpZiAocGxheWVyLnBhdXNlZCAmJiAhZm9yY2VFdmVudHMpIHtcblx0XHRyZXR1cm47XG5cdH1cblxuXHRwbGF5ZXIucGF1c2VkID0gdHJ1ZTtcblx0aWYgKCFwbGF5ZXIuaGFzQXVkaW8pIHtcblx0XHRkaXNwYXRjaEV2ZW50QXN5bmModmlkZW8sICdwYXVzZScpO1xuXHR9XG5cdGlmICh2aWRlby5lbmRlZCkge1xuXHRcdHZpZGVvW+CyoGV2ZW50XSA9IHRydWU7XG5cdFx0ZGlzcGF0Y2hFdmVudEFzeW5jKHZpZGVvLCAnZW5kZWQnKTtcblx0fVxufVxuXG4vKipcbiAqIFNFVFVQXG4gKi9cblxuZnVuY3Rpb24gYWRkUGxheWVyKHZpZGVvLCBoYXNBdWRpbykge1xuXHR2YXIgcGxheWVyID0gdmlkZW9b4LKgXSA9IHt9O1xuXHRwbGF5ZXIucGF1c2VkID0gdHJ1ZTsgLy8gdHJhY2sgd2hldGhlciAncGF1c2UnIGV2ZW50cyBoYXZlIGJlZW4gZmlyZWRcblx0cGxheWVyLmhhc0F1ZGlvID0gaGFzQXVkaW87XG5cdHBsYXllci52aWRlbyA9IHZpZGVvO1xuXHRwbGF5ZXIudXBkYXRlciA9IGludGVydmFsb21ldGVyLmZyYW1lSW50ZXJ2YWxvbWV0ZXIodXBkYXRlLmJpbmQocGxheWVyKSk7XG5cblx0aWYgKGhhc0F1ZGlvKSB7XG5cdFx0cGxheWVyLmRyaXZlciA9IGdldEF1ZGlvRnJvbVZpZGVvKHZpZGVvKTtcblx0fSBlbHNlIHtcblx0XHR2aWRlby5hZGRFdmVudExpc3RlbmVyKCdjYW5wbGF5JywgZnVuY3Rpb24gKCkge1xuXHRcdFx0aWYgKCF2aWRlby5wYXVzZWQpIHtcblx0XHRcdFx0Ly8gY29uc29sZS5sb2coJ29uY2FucGxheScpO1xuXHRcdFx0XHRkaXNwYXRjaEV2ZW50QXN5bmModmlkZW8sICdwbGF5aW5nJyk7XG5cdFx0XHR9XG5cdFx0fSk7XG5cdFx0cGxheWVyLmRyaXZlciA9IHtcblx0XHRcdHNyYzogdmlkZW8uc3JjIHx8IHZpZGVvLmN1cnJlbnRTcmMgfHwgJ2RhdGE6Jyxcblx0XHRcdG11dGVkOiB0cnVlLFxuXHRcdFx0cGF1c2VkOiB0cnVlLFxuXHRcdFx0cGF1c2U6IGZ1bmN0aW9uICgpIHtcblx0XHRcdFx0cGxheWVyLmRyaXZlci5wYXVzZWQgPSB0cnVlO1xuXHRcdFx0fSxcblx0XHRcdHBsYXk6IGZ1bmN0aW9uICgpIHtcblx0XHRcdFx0cGxheWVyLmRyaXZlci5wYXVzZWQgPSBmYWxzZTtcblx0XHRcdFx0Ly8gbWVkaWEgYXV0b21hdGljYWxseSBnb2VzIHRvIDAgaWYgLnBsYXkoKSBpcyBjYWxsZWQgd2hlbiBpdCdzIGRvbmVcblx0XHRcdFx0aWYgKGlzUGxheWVyRW5kZWQocGxheWVyKSkge1xuXHRcdFx0XHRcdHNldFRpbWUodmlkZW8sIDApO1xuXHRcdFx0XHR9XG5cdFx0XHR9LFxuXHRcdFx0Z2V0IGVuZGVkKCkge1xuXHRcdFx0XHRyZXR1cm4gaXNQbGF5ZXJFbmRlZChwbGF5ZXIpO1xuXHRcdFx0fVxuXHRcdH07XG5cdH1cblxuXHQvLyAubG9hZCgpIGNhdXNlcyB0aGUgZW1wdGllZCBldmVudFxuXHR2aWRlby5hZGRFdmVudExpc3RlbmVyKCdlbXB0aWVkJywgZnVuY3Rpb24gKCkge1xuXHRcdC8vIGNvbnNvbGUubG9nKCdkcml2ZXIgc3JjIGlzJywgcGxheWVyLmRyaXZlci5zcmMpO1xuXHRcdHZhciB3YXNFbXB0eSA9ICFwbGF5ZXIuZHJpdmVyLnNyYyB8fCBwbGF5ZXIuZHJpdmVyLnNyYyA9PT0gJ2RhdGE6Jztcblx0XHRpZiAocGxheWVyLmRyaXZlci5zcmMgJiYgcGxheWVyLmRyaXZlci5zcmMgIT09IHZpZGVvLnNyYykge1xuXHRcdFx0Ly8gY29uc29sZS5sb2coJ3NyYyBjaGFuZ2VkIHRvJywgdmlkZW8uc3JjKTtcblx0XHRcdHNldFRpbWUodmlkZW8sIDAsIHRydWUpO1xuXHRcdFx0cGxheWVyLmRyaXZlci5zcmMgPSB2aWRlby5zcmM7XG5cdFx0XHQvLyBwbGF5aW5nIHZpZGVvcyB3aWxsIG9ubHkga2VlcCBwbGF5aW5nIGlmIG5vIHNyYyB3YXMgcHJlc2VudCB3aGVuIC5wbGF5KCnigJllZFxuXHRcdFx0aWYgKHdhc0VtcHR5KSB7XG5cdFx0XHRcdHBsYXllci5kcml2ZXIucGxheSgpO1xuXHRcdFx0fSBlbHNlIHtcblx0XHRcdFx0cGxheWVyLnVwZGF0ZXIuc3RvcCgpO1xuXHRcdFx0fVxuXHRcdH1cblx0fSwgZmFsc2UpO1xuXG5cdC8vIHN0b3AgcHJvZ3JhbW1hdGljIHBsYXllciB3aGVuIE9TIHRha2VzIG92ZXJcblx0dmlkZW8uYWRkRXZlbnRMaXN0ZW5lcignd2Via2l0YmVnaW5mdWxsc2NyZWVuJywgZnVuY3Rpb24gKCkge1xuXHRcdGlmICghdmlkZW8ucGF1c2VkKSB7XG5cdFx0XHQvLyBtYWtlIHN1cmUgdGhhdCB0aGUgPGF1ZGlvPiBhbmQgdGhlIHN5bmNlci91cGRhdGVyIGFyZSBzdG9wcGVkXG5cdFx0XHR2aWRlby5wYXVzZSgpO1xuXG5cdFx0XHQvLyBwbGF5IHZpZGVvIG5hdGl2ZWx5XG5cdFx0XHR2aWRlb1vgsqBwbGF5XSgpO1xuXHRcdH0gZWxzZSBpZiAoaGFzQXVkaW8gJiYgIXBsYXllci5kcml2ZXIuYnVmZmVyZWQubGVuZ3RoKSB7XG5cdFx0XHQvLyBpZiB0aGUgZmlyc3QgcGxheSBpcyBuYXRpdmUsXG5cdFx0XHQvLyB0aGUgPGF1ZGlvPiBuZWVkcyB0byBiZSBidWZmZXJlZCBtYW51YWxseVxuXHRcdFx0Ly8gc28gd2hlbiB0aGUgZnVsbHNjcmVlbiBlbmRzLCBpdCBjYW4gYmUgc2V0IHRvIHRoZSBzYW1lIGN1cnJlbnQgdGltZVxuXHRcdFx0cGxheWVyLmRyaXZlci5sb2FkKCk7XG5cdFx0fVxuXHR9KTtcblx0aWYgKGhhc0F1ZGlvKSB7XG5cdFx0dmlkZW8uYWRkRXZlbnRMaXN0ZW5lcignd2Via2l0ZW5kZnVsbHNjcmVlbicsIGZ1bmN0aW9uICgpIHtcblx0XHRcdC8vIHN5bmMgYXVkaW8gdG8gbmV3IHZpZGVvIHBvc2l0aW9uXG5cdFx0XHRwbGF5ZXIuZHJpdmVyLmN1cnJlbnRUaW1lID0gdmlkZW8uY3VycmVudFRpbWU7XG5cdFx0XHQvLyBjb25zb2xlLmFzc2VydChwbGF5ZXIuZHJpdmVyLmN1cnJlbnRUaW1lID09PSB2aWRlby5jdXJyZW50VGltZSwgJ0F1ZGlvIG5vdCBzeW5jZWQnKTtcblx0XHR9KTtcblxuXHRcdC8vIGFsbG93IHNlZWtpbmdcblx0XHR2aWRlby5hZGRFdmVudExpc3RlbmVyKCdzZWVraW5nJywgZnVuY3Rpb24gKCkge1xuXHRcdFx0aWYgKGxhc3RSZXF1ZXN0cy5pbmRleE9mKHZpZGVvLmN1cnJlbnRUaW1lICogMTAwIHwgMCAvIDEwMCkgPCAwKSB7XG5cdFx0XHRcdC8vIGNvbnNvbGUubG9nKCdVc2VyLXJlcXVlc3RlZCBzZWVraW5nJyk7XG5cdFx0XHRcdHBsYXllci5kcml2ZXIuY3VycmVudFRpbWUgPSB2aWRlby5jdXJyZW50VGltZTtcblx0XHRcdH1cblx0XHR9KTtcblx0fVxufVxuXG5mdW5jdGlvbiBvdmVybG9hZEFQSSh2aWRlbykge1xuXHR2YXIgcGxheWVyID0gdmlkZW9b4LKgXTtcblx0dmlkZW9b4LKgcGxheV0gPSB2aWRlby5wbGF5O1xuXHR2aWRlb1vgsqBwYXVzZV0gPSB2aWRlby5wYXVzZTtcblx0dmlkZW8ucGxheSA9IHBsYXk7XG5cdHZpZGVvLnBhdXNlID0gcGF1c2U7XG5cdHByb3h5UHJvcGVydHkodmlkZW8sICdwYXVzZWQnLCBwbGF5ZXIuZHJpdmVyKTtcblx0cHJveHlQcm9wZXJ0eSh2aWRlbywgJ211dGVkJywgcGxheWVyLmRyaXZlciwgdHJ1ZSk7XG5cdHByb3h5UHJvcGVydHkodmlkZW8sICdwbGF5YmFja1JhdGUnLCBwbGF5ZXIuZHJpdmVyLCB0cnVlKTtcblx0cHJveHlQcm9wZXJ0eSh2aWRlbywgJ2VuZGVkJywgcGxheWVyLmRyaXZlcik7XG5cdHByb3h5UHJvcGVydHkodmlkZW8sICdsb29wJywgcGxheWVyLmRyaXZlciwgdHJ1ZSk7XG5cdHByZXZlbnRFdmVudCh2aWRlbywgJ3NlZWtpbmcnKTtcblx0cHJldmVudEV2ZW50KHZpZGVvLCAnc2Vla2VkJyk7XG5cdHByZXZlbnRFdmVudCh2aWRlbywgJ3RpbWV1cGRhdGUnLCDgsqBldmVudCwgZmFsc2UpO1xuXHRwcmV2ZW50RXZlbnQodmlkZW8sICdlbmRlZCcsIOCyoGV2ZW50LCBmYWxzZSk7IC8vIHByZXZlbnQgb2NjYXNpb25hbCBuYXRpdmUgZW5kZWQgZXZlbnRzXG59XG5cbmZ1bmN0aW9uIGVuYWJsZUlubGluZVZpZGVvKHZpZGVvLCBoYXNBdWRpbywgb25seVdoaXRlbGlzdGVkKSB7XG5cdGlmICggaGFzQXVkaW8gPT09IHZvaWQgMCApIGhhc0F1ZGlvID0gdHJ1ZTtcblx0aWYgKCBvbmx5V2hpdGVsaXN0ZWQgPT09IHZvaWQgMCApIG9ubHlXaGl0ZWxpc3RlZCA9IHRydWU7XG5cblx0aWYgKChvbmx5V2hpdGVsaXN0ZWQgJiYgIWlzV2hpdGVsaXN0ZWQpIHx8IHZpZGVvW+CyoF0pIHtcblx0XHRyZXR1cm47XG5cdH1cblx0YWRkUGxheWVyKHZpZGVvLCBoYXNBdWRpbyk7XG5cdG92ZXJsb2FkQVBJKHZpZGVvKTtcblx0dmlkZW8uY2xhc3NMaXN0LmFkZCgnSUlWJyk7XG5cdGlmICghaGFzQXVkaW8gJiYgdmlkZW8uYXV0b3BsYXkpIHtcblx0XHR2aWRlby5wbGF5KCk7XG5cdH1cblx0aWYgKCEvaVBob25lfGlQb2R8aVBhZC8udGVzdChuYXZpZ2F0b3IucGxhdGZvcm0pKSB7XG5cdFx0Y29uc29sZS53YXJuKCdpcGhvbmUtaW5saW5lLXZpZGVvIGlzIG5vdCBndWFyYW50ZWVkIHRvIHdvcmsgaW4gZW11bGF0ZWQgZW52aXJvbm1lbnRzJyk7XG5cdH1cbn1cblxuZW5hYmxlSW5saW5lVmlkZW8uaXNXaGl0ZWxpc3RlZCA9IGlzV2hpdGVsaXN0ZWQ7XG5cbm1vZHVsZS5leHBvcnRzID0gZW5hYmxlSW5saW5lVmlkZW87IiwiJ3VzZSBzdHJpY3QnO1xuXG52YXIgaW5kZXggPSB0eXBlb2YgU3ltYm9sID09PSAndW5kZWZpbmVkJyA/IGZ1bmN0aW9uIChkZXNjcmlwdGlvbikge1xuXHRyZXR1cm4gJ0AnICsgKGRlc2NyaXB0aW9uIHx8ICdAJykgKyBNYXRoLnJhbmRvbSgpO1xufSA6IFN5bWJvbDtcblxubW9kdWxlLmV4cG9ydHMgPSBpbmRleDsiLCIvKiFcbiAqIEV2ZW50RW1pdHRlciB2NS4xLjAgLSBnaXQuaW8vZWVcbiAqIFVubGljZW5zZSAtIGh0dHA6Ly91bmxpY2Vuc2Uub3JnL1xuICogT2xpdmVyIENhbGR3ZWxsIC0gaHR0cDovL29saS5tZS51ay9cbiAqIEBwcmVzZXJ2ZVxuICovXG5cbjsoZnVuY3Rpb24gKGV4cG9ydHMpIHtcbiAgICAndXNlIHN0cmljdCc7XG5cbiAgICAvKipcbiAgICAgKiBDbGFzcyBmb3IgbWFuYWdpbmcgZXZlbnRzLlxuICAgICAqIENhbiBiZSBleHRlbmRlZCB0byBwcm92aWRlIGV2ZW50IGZ1bmN0aW9uYWxpdHkgaW4gb3RoZXIgY2xhc3Nlcy5cbiAgICAgKlxuICAgICAqIEBjbGFzcyBFdmVudEVtaXR0ZXIgTWFuYWdlcyBldmVudCByZWdpc3RlcmluZyBhbmQgZW1pdHRpbmcuXG4gICAgICovXG4gICAgZnVuY3Rpb24gRXZlbnRFbWl0dGVyKCkge31cblxuICAgIC8vIFNob3J0Y3V0cyB0byBpbXByb3ZlIHNwZWVkIGFuZCBzaXplXG4gICAgdmFyIHByb3RvID0gRXZlbnRFbWl0dGVyLnByb3RvdHlwZTtcbiAgICB2YXIgb3JpZ2luYWxHbG9iYWxWYWx1ZSA9IGV4cG9ydHMuRXZlbnRFbWl0dGVyO1xuXG4gICAgLyoqXG4gICAgICogRmluZHMgdGhlIGluZGV4IG9mIHRoZSBsaXN0ZW5lciBmb3IgdGhlIGV2ZW50IGluIGl0cyBzdG9yYWdlIGFycmF5LlxuICAgICAqXG4gICAgICogQHBhcmFtIHtGdW5jdGlvbltdfSBsaXN0ZW5lcnMgQXJyYXkgb2YgbGlzdGVuZXJzIHRvIHNlYXJjaCB0aHJvdWdoLlxuICAgICAqIEBwYXJhbSB7RnVuY3Rpb259IGxpc3RlbmVyIE1ldGhvZCB0byBsb29rIGZvci5cbiAgICAgKiBAcmV0dXJuIHtOdW1iZXJ9IEluZGV4IG9mIHRoZSBzcGVjaWZpZWQgbGlzdGVuZXIsIC0xIGlmIG5vdCBmb3VuZFxuICAgICAqIEBhcGkgcHJpdmF0ZVxuICAgICAqL1xuICAgIGZ1bmN0aW9uIGluZGV4T2ZMaXN0ZW5lcihsaXN0ZW5lcnMsIGxpc3RlbmVyKSB7XG4gICAgICAgIHZhciBpID0gbGlzdGVuZXJzLmxlbmd0aDtcbiAgICAgICAgd2hpbGUgKGktLSkge1xuICAgICAgICAgICAgaWYgKGxpc3RlbmVyc1tpXS5saXN0ZW5lciA9PT0gbGlzdGVuZXIpIHtcbiAgICAgICAgICAgICAgICByZXR1cm4gaTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiAtMTtcbiAgICB9XG5cbiAgICAvKipcbiAgICAgKiBBbGlhcyBhIG1ldGhvZCB3aGlsZSBrZWVwaW5nIHRoZSBjb250ZXh0IGNvcnJlY3QsIHRvIGFsbG93IGZvciBvdmVyd3JpdGluZyBvZiB0YXJnZXQgbWV0aG9kLlxuICAgICAqXG4gICAgICogQHBhcmFtIHtTdHJpbmd9IG5hbWUgVGhlIG5hbWUgb2YgdGhlIHRhcmdldCBtZXRob2QuXG4gICAgICogQHJldHVybiB7RnVuY3Rpb259IFRoZSBhbGlhc2VkIG1ldGhvZFxuICAgICAqIEBhcGkgcHJpdmF0ZVxuICAgICAqL1xuICAgIGZ1bmN0aW9uIGFsaWFzKG5hbWUpIHtcbiAgICAgICAgcmV0dXJuIGZ1bmN0aW9uIGFsaWFzQ2xvc3VyZSgpIHtcbiAgICAgICAgICAgIHJldHVybiB0aGlzW25hbWVdLmFwcGx5KHRoaXMsIGFyZ3VtZW50cyk7XG4gICAgICAgIH07XG4gICAgfVxuXG4gICAgLyoqXG4gICAgICogUmV0dXJucyB0aGUgbGlzdGVuZXIgYXJyYXkgZm9yIHRoZSBzcGVjaWZpZWQgZXZlbnQuXG4gICAgICogV2lsbCBpbml0aWFsaXNlIHRoZSBldmVudCBvYmplY3QgYW5kIGxpc3RlbmVyIGFycmF5cyBpZiByZXF1aXJlZC5cbiAgICAgKiBXaWxsIHJldHVybiBhbiBvYmplY3QgaWYgeW91IHVzZSBhIHJlZ2V4IHNlYXJjaC4gVGhlIG9iamVjdCBjb250YWlucyBrZXlzIGZvciBlYWNoIG1hdGNoZWQgZXZlbnQuIFNvIC9iYVtyel0vIG1pZ2h0IHJldHVybiBhbiBvYmplY3QgY29udGFpbmluZyBiYXIgYW5kIGJhei4gQnV0IG9ubHkgaWYgeW91IGhhdmUgZWl0aGVyIGRlZmluZWQgdGhlbSB3aXRoIGRlZmluZUV2ZW50IG9yIGFkZGVkIHNvbWUgbGlzdGVuZXJzIHRvIHRoZW0uXG4gICAgICogRWFjaCBwcm9wZXJ0eSBpbiB0aGUgb2JqZWN0IHJlc3BvbnNlIGlzIGFuIGFycmF5IG9mIGxpc3RlbmVyIGZ1bmN0aW9ucy5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfFJlZ0V4cH0gZXZ0IE5hbWUgb2YgdGhlIGV2ZW50IHRvIHJldHVybiB0aGUgbGlzdGVuZXJzIGZyb20uXG4gICAgICogQHJldHVybiB7RnVuY3Rpb25bXXxPYmplY3R9IEFsbCBsaXN0ZW5lciBmdW5jdGlvbnMgZm9yIHRoZSBldmVudC5cbiAgICAgKi9cbiAgICBwcm90by5nZXRMaXN0ZW5lcnMgPSBmdW5jdGlvbiBnZXRMaXN0ZW5lcnMoZXZ0KSB7XG4gICAgICAgIHZhciBldmVudHMgPSB0aGlzLl9nZXRFdmVudHMoKTtcbiAgICAgICAgdmFyIHJlc3BvbnNlO1xuICAgICAgICB2YXIga2V5O1xuXG4gICAgICAgIC8vIFJldHVybiBhIGNvbmNhdGVuYXRlZCBhcnJheSBvZiBhbGwgbWF0Y2hpbmcgZXZlbnRzIGlmXG4gICAgICAgIC8vIHRoZSBzZWxlY3RvciBpcyBhIHJlZ3VsYXIgZXhwcmVzc2lvbi5cbiAgICAgICAgaWYgKGV2dCBpbnN0YW5jZW9mIFJlZ0V4cCkge1xuICAgICAgICAgICAgcmVzcG9uc2UgPSB7fTtcbiAgICAgICAgICAgIGZvciAoa2V5IGluIGV2ZW50cykge1xuICAgICAgICAgICAgICAgIGlmIChldmVudHMuaGFzT3duUHJvcGVydHkoa2V5KSAmJiBldnQudGVzdChrZXkpKSB7XG4gICAgICAgICAgICAgICAgICAgIHJlc3BvbnNlW2tleV0gPSBldmVudHNba2V5XTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgZWxzZSB7XG4gICAgICAgICAgICByZXNwb25zZSA9IGV2ZW50c1tldnRdIHx8IChldmVudHNbZXZ0XSA9IFtdKTtcbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiByZXNwb25zZTtcbiAgICB9O1xuXG4gICAgLyoqXG4gICAgICogVGFrZXMgYSBsaXN0IG9mIGxpc3RlbmVyIG9iamVjdHMgYW5kIGZsYXR0ZW5zIGl0IGludG8gYSBsaXN0IG9mIGxpc3RlbmVyIGZ1bmN0aW9ucy5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7T2JqZWN0W119IGxpc3RlbmVycyBSYXcgbGlzdGVuZXIgb2JqZWN0cy5cbiAgICAgKiBAcmV0dXJuIHtGdW5jdGlvbltdfSBKdXN0IHRoZSBsaXN0ZW5lciBmdW5jdGlvbnMuXG4gICAgICovXG4gICAgcHJvdG8uZmxhdHRlbkxpc3RlbmVycyA9IGZ1bmN0aW9uIGZsYXR0ZW5MaXN0ZW5lcnMobGlzdGVuZXJzKSB7XG4gICAgICAgIHZhciBmbGF0TGlzdGVuZXJzID0gW107XG4gICAgICAgIHZhciBpO1xuXG4gICAgICAgIGZvciAoaSA9IDA7IGkgPCBsaXN0ZW5lcnMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgIGZsYXRMaXN0ZW5lcnMucHVzaChsaXN0ZW5lcnNbaV0ubGlzdGVuZXIpO1xuICAgICAgICB9XG5cbiAgICAgICAgcmV0dXJuIGZsYXRMaXN0ZW5lcnM7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIEZldGNoZXMgdGhlIHJlcXVlc3RlZCBsaXN0ZW5lcnMgdmlhIGdldExpc3RlbmVycyBidXQgd2lsbCBhbHdheXMgcmV0dXJuIHRoZSByZXN1bHRzIGluc2lkZSBhbiBvYmplY3QuIFRoaXMgaXMgbWFpbmx5IGZvciBpbnRlcm5hbCB1c2UgYnV0IG90aGVycyBtYXkgZmluZCBpdCB1c2VmdWwuXG4gICAgICpcbiAgICAgKiBAcGFyYW0ge1N0cmluZ3xSZWdFeHB9IGV2dCBOYW1lIG9mIHRoZSBldmVudCB0byByZXR1cm4gdGhlIGxpc3RlbmVycyBmcm9tLlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQWxsIGxpc3RlbmVyIGZ1bmN0aW9ucyBmb3IgYW4gZXZlbnQgaW4gYW4gb2JqZWN0LlxuICAgICAqL1xuICAgIHByb3RvLmdldExpc3RlbmVyc0FzT2JqZWN0ID0gZnVuY3Rpb24gZ2V0TGlzdGVuZXJzQXNPYmplY3QoZXZ0KSB7XG4gICAgICAgIHZhciBsaXN0ZW5lcnMgPSB0aGlzLmdldExpc3RlbmVycyhldnQpO1xuICAgICAgICB2YXIgcmVzcG9uc2U7XG5cbiAgICAgICAgaWYgKGxpc3RlbmVycyBpbnN0YW5jZW9mIEFycmF5KSB7XG4gICAgICAgICAgICByZXNwb25zZSA9IHt9O1xuICAgICAgICAgICAgcmVzcG9uc2VbZXZ0XSA9IGxpc3RlbmVycztcbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiByZXNwb25zZSB8fCBsaXN0ZW5lcnM7XG4gICAgfTtcblxuICAgIGZ1bmN0aW9uIGlzVmFsaWRMaXN0ZW5lciAobGlzdGVuZXIpIHtcbiAgICAgICAgaWYgKHR5cGVvZiBsaXN0ZW5lciA9PT0gJ2Z1bmN0aW9uJyB8fCBsaXN0ZW5lciBpbnN0YW5jZW9mIFJlZ0V4cCkge1xuICAgICAgICAgICAgcmV0dXJuIHRydWVcbiAgICAgICAgfSBlbHNlIGlmIChsaXN0ZW5lciAmJiB0eXBlb2YgbGlzdGVuZXIgPT09ICdvYmplY3QnKSB7XG4gICAgICAgICAgICByZXR1cm4gaXNWYWxpZExpc3RlbmVyKGxpc3RlbmVyLmxpc3RlbmVyKVxuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgcmV0dXJuIGZhbHNlXG4gICAgICAgIH1cbiAgICB9XG5cbiAgICAvKipcbiAgICAgKiBBZGRzIGEgbGlzdGVuZXIgZnVuY3Rpb24gdG8gdGhlIHNwZWNpZmllZCBldmVudC5cbiAgICAgKiBUaGUgbGlzdGVuZXIgd2lsbCBub3QgYmUgYWRkZWQgaWYgaXQgaXMgYSBkdXBsaWNhdGUuXG4gICAgICogSWYgdGhlIGxpc3RlbmVyIHJldHVybnMgdHJ1ZSB0aGVuIGl0IHdpbGwgYmUgcmVtb3ZlZCBhZnRlciBpdCBpcyBjYWxsZWQuXG4gICAgICogSWYgeW91IHBhc3MgYSByZWd1bGFyIGV4cHJlc3Npb24gYXMgdGhlIGV2ZW50IG5hbWUgdGhlbiB0aGUgbGlzdGVuZXIgd2lsbCBiZSBhZGRlZCB0byBhbGwgZXZlbnRzIHRoYXQgbWF0Y2ggaXQuXG4gICAgICpcbiAgICAgKiBAcGFyYW0ge1N0cmluZ3xSZWdFeHB9IGV2dCBOYW1lIG9mIHRoZSBldmVudCB0byBhdHRhY2ggdGhlIGxpc3RlbmVyIHRvLlxuICAgICAqIEBwYXJhbSB7RnVuY3Rpb259IGxpc3RlbmVyIE1ldGhvZCB0byBiZSBjYWxsZWQgd2hlbiB0aGUgZXZlbnQgaXMgZW1pdHRlZC4gSWYgdGhlIGZ1bmN0aW9uIHJldHVybnMgdHJ1ZSB0aGVuIGl0IHdpbGwgYmUgcmVtb3ZlZCBhZnRlciBjYWxsaW5nLlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQ3VycmVudCBpbnN0YW5jZSBvZiBFdmVudEVtaXR0ZXIgZm9yIGNoYWluaW5nLlxuICAgICAqL1xuICAgIHByb3RvLmFkZExpc3RlbmVyID0gZnVuY3Rpb24gYWRkTGlzdGVuZXIoZXZ0LCBsaXN0ZW5lcikge1xuICAgICAgICBpZiAoIWlzVmFsaWRMaXN0ZW5lcihsaXN0ZW5lcikpIHtcbiAgICAgICAgICAgIHRocm93IG5ldyBUeXBlRXJyb3IoJ2xpc3RlbmVyIG11c3QgYmUgYSBmdW5jdGlvbicpO1xuICAgICAgICB9XG5cbiAgICAgICAgdmFyIGxpc3RlbmVycyA9IHRoaXMuZ2V0TGlzdGVuZXJzQXNPYmplY3QoZXZ0KTtcbiAgICAgICAgdmFyIGxpc3RlbmVySXNXcmFwcGVkID0gdHlwZW9mIGxpc3RlbmVyID09PSAnb2JqZWN0JztcbiAgICAgICAgdmFyIGtleTtcblxuICAgICAgICBmb3IgKGtleSBpbiBsaXN0ZW5lcnMpIHtcbiAgICAgICAgICAgIGlmIChsaXN0ZW5lcnMuaGFzT3duUHJvcGVydHkoa2V5KSAmJiBpbmRleE9mTGlzdGVuZXIobGlzdGVuZXJzW2tleV0sIGxpc3RlbmVyKSA9PT0gLTEpIHtcbiAgICAgICAgICAgICAgICBsaXN0ZW5lcnNba2V5XS5wdXNoKGxpc3RlbmVySXNXcmFwcGVkID8gbGlzdGVuZXIgOiB7XG4gICAgICAgICAgICAgICAgICAgIGxpc3RlbmVyOiBsaXN0ZW5lcixcbiAgICAgICAgICAgICAgICAgICAgb25jZTogZmFsc2VcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiB0aGlzO1xuICAgIH07XG5cbiAgICAvKipcbiAgICAgKiBBbGlhcyBvZiBhZGRMaXN0ZW5lclxuICAgICAqL1xuICAgIHByb3RvLm9uID0gYWxpYXMoJ2FkZExpc3RlbmVyJyk7XG5cbiAgICAvKipcbiAgICAgKiBTZW1pLWFsaWFzIG9mIGFkZExpc3RlbmVyLiBJdCB3aWxsIGFkZCBhIGxpc3RlbmVyIHRoYXQgd2lsbCBiZVxuICAgICAqIGF1dG9tYXRpY2FsbHkgcmVtb3ZlZCBhZnRlciBpdHMgZmlyc3QgZXhlY3V0aW9uLlxuICAgICAqXG4gICAgICogQHBhcmFtIHtTdHJpbmd8UmVnRXhwfSBldnQgTmFtZSBvZiB0aGUgZXZlbnQgdG8gYXR0YWNoIHRoZSBsaXN0ZW5lciB0by5cbiAgICAgKiBAcGFyYW0ge0Z1bmN0aW9ufSBsaXN0ZW5lciBNZXRob2QgdG8gYmUgY2FsbGVkIHdoZW4gdGhlIGV2ZW50IGlzIGVtaXR0ZWQuIElmIHRoZSBmdW5jdGlvbiByZXR1cm5zIHRydWUgdGhlbiBpdCB3aWxsIGJlIHJlbW92ZWQgYWZ0ZXIgY2FsbGluZy5cbiAgICAgKiBAcmV0dXJuIHtPYmplY3R9IEN1cnJlbnQgaW5zdGFuY2Ugb2YgRXZlbnRFbWl0dGVyIGZvciBjaGFpbmluZy5cbiAgICAgKi9cbiAgICBwcm90by5hZGRPbmNlTGlzdGVuZXIgPSBmdW5jdGlvbiBhZGRPbmNlTGlzdGVuZXIoZXZ0LCBsaXN0ZW5lcikge1xuICAgICAgICByZXR1cm4gdGhpcy5hZGRMaXN0ZW5lcihldnQsIHtcbiAgICAgICAgICAgIGxpc3RlbmVyOiBsaXN0ZW5lcixcbiAgICAgICAgICAgIG9uY2U6IHRydWVcbiAgICAgICAgfSk7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIEFsaWFzIG9mIGFkZE9uY2VMaXN0ZW5lci5cbiAgICAgKi9cbiAgICBwcm90by5vbmNlID0gYWxpYXMoJ2FkZE9uY2VMaXN0ZW5lcicpO1xuXG4gICAgLyoqXG4gICAgICogRGVmaW5lcyBhbiBldmVudCBuYW1lLiBUaGlzIGlzIHJlcXVpcmVkIGlmIHlvdSB3YW50IHRvIHVzZSBhIHJlZ2V4IHRvIGFkZCBhIGxpc3RlbmVyIHRvIG11bHRpcGxlIGV2ZW50cyBhdCBvbmNlLiBJZiB5b3UgZG9uJ3QgZG8gdGhpcyB0aGVuIGhvdyBkbyB5b3UgZXhwZWN0IGl0IHRvIGtub3cgd2hhdCBldmVudCB0byBhZGQgdG8/IFNob3VsZCBpdCBqdXN0IGFkZCB0byBldmVyeSBwb3NzaWJsZSBtYXRjaCBmb3IgYSByZWdleD8gTm8uIFRoYXQgaXMgc2NhcnkgYW5kIGJhZC5cbiAgICAgKiBZb3UgbmVlZCB0byB0ZWxsIGl0IHdoYXQgZXZlbnQgbmFtZXMgc2hvdWxkIGJlIG1hdGNoZWQgYnkgYSByZWdleC5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfSBldnQgTmFtZSBvZiB0aGUgZXZlbnQgdG8gY3JlYXRlLlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQ3VycmVudCBpbnN0YW5jZSBvZiBFdmVudEVtaXR0ZXIgZm9yIGNoYWluaW5nLlxuICAgICAqL1xuICAgIHByb3RvLmRlZmluZUV2ZW50ID0gZnVuY3Rpb24gZGVmaW5lRXZlbnQoZXZ0KSB7XG4gICAgICAgIHRoaXMuZ2V0TGlzdGVuZXJzKGV2dCk7XG4gICAgICAgIHJldHVybiB0aGlzO1xuICAgIH07XG5cbiAgICAvKipcbiAgICAgKiBVc2VzIGRlZmluZUV2ZW50IHRvIGRlZmluZSBtdWx0aXBsZSBldmVudHMuXG4gICAgICpcbiAgICAgKiBAcGFyYW0ge1N0cmluZ1tdfSBldnRzIEFuIGFycmF5IG9mIGV2ZW50IG5hbWVzIHRvIGRlZmluZS5cbiAgICAgKiBAcmV0dXJuIHtPYmplY3R9IEN1cnJlbnQgaW5zdGFuY2Ugb2YgRXZlbnRFbWl0dGVyIGZvciBjaGFpbmluZy5cbiAgICAgKi9cbiAgICBwcm90by5kZWZpbmVFdmVudHMgPSBmdW5jdGlvbiBkZWZpbmVFdmVudHMoZXZ0cykge1xuICAgICAgICBmb3IgKHZhciBpID0gMDsgaSA8IGV2dHMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgIHRoaXMuZGVmaW5lRXZlbnQoZXZ0c1tpXSk7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIHRoaXM7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIFJlbW92ZXMgYSBsaXN0ZW5lciBmdW5jdGlvbiBmcm9tIHRoZSBzcGVjaWZpZWQgZXZlbnQuXG4gICAgICogV2hlbiBwYXNzZWQgYSByZWd1bGFyIGV4cHJlc3Npb24gYXMgdGhlIGV2ZW50IG5hbWUsIGl0IHdpbGwgcmVtb3ZlIHRoZSBsaXN0ZW5lciBmcm9tIGFsbCBldmVudHMgdGhhdCBtYXRjaCBpdC5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfFJlZ0V4cH0gZXZ0IE5hbWUgb2YgdGhlIGV2ZW50IHRvIHJlbW92ZSB0aGUgbGlzdGVuZXIgZnJvbS5cbiAgICAgKiBAcGFyYW0ge0Z1bmN0aW9ufSBsaXN0ZW5lciBNZXRob2QgdG8gcmVtb3ZlIGZyb20gdGhlIGV2ZW50LlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQ3VycmVudCBpbnN0YW5jZSBvZiBFdmVudEVtaXR0ZXIgZm9yIGNoYWluaW5nLlxuICAgICAqL1xuICAgIHByb3RvLnJlbW92ZUxpc3RlbmVyID0gZnVuY3Rpb24gcmVtb3ZlTGlzdGVuZXIoZXZ0LCBsaXN0ZW5lcikge1xuICAgICAgICB2YXIgbGlzdGVuZXJzID0gdGhpcy5nZXRMaXN0ZW5lcnNBc09iamVjdChldnQpO1xuICAgICAgICB2YXIgaW5kZXg7XG4gICAgICAgIHZhciBrZXk7XG5cbiAgICAgICAgZm9yIChrZXkgaW4gbGlzdGVuZXJzKSB7XG4gICAgICAgICAgICBpZiAobGlzdGVuZXJzLmhhc093blByb3BlcnR5KGtleSkpIHtcbiAgICAgICAgICAgICAgICBpbmRleCA9IGluZGV4T2ZMaXN0ZW5lcihsaXN0ZW5lcnNba2V5XSwgbGlzdGVuZXIpO1xuXG4gICAgICAgICAgICAgICAgaWYgKGluZGV4ICE9PSAtMSkge1xuICAgICAgICAgICAgICAgICAgICBsaXN0ZW5lcnNba2V5XS5zcGxpY2UoaW5kZXgsIDEpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiB0aGlzO1xuICAgIH07XG5cbiAgICAvKipcbiAgICAgKiBBbGlhcyBvZiByZW1vdmVMaXN0ZW5lclxuICAgICAqL1xuICAgIHByb3RvLm9mZiA9IGFsaWFzKCdyZW1vdmVMaXN0ZW5lcicpO1xuXG4gICAgLyoqXG4gICAgICogQWRkcyBsaXN0ZW5lcnMgaW4gYnVsayB1c2luZyB0aGUgbWFuaXB1bGF0ZUxpc3RlbmVycyBtZXRob2QuXG4gICAgICogSWYgeW91IHBhc3MgYW4gb2JqZWN0IGFzIHRoZSBzZWNvbmQgYXJndW1lbnQgeW91IGNhbiBhZGQgdG8gbXVsdGlwbGUgZXZlbnRzIGF0IG9uY2UuIFRoZSBvYmplY3Qgc2hvdWxkIGNvbnRhaW4ga2V5IHZhbHVlIHBhaXJzIG9mIGV2ZW50cyBhbmQgbGlzdGVuZXJzIG9yIGxpc3RlbmVyIGFycmF5cy4gWW91IGNhbiBhbHNvIHBhc3MgaXQgYW4gZXZlbnQgbmFtZSBhbmQgYW4gYXJyYXkgb2YgbGlzdGVuZXJzIHRvIGJlIGFkZGVkLlxuICAgICAqIFlvdSBjYW4gYWxzbyBwYXNzIGl0IGEgcmVndWxhciBleHByZXNzaW9uIHRvIGFkZCB0aGUgYXJyYXkgb2YgbGlzdGVuZXJzIHRvIGFsbCBldmVudHMgdGhhdCBtYXRjaCBpdC5cbiAgICAgKiBZZWFoLCB0aGlzIGZ1bmN0aW9uIGRvZXMgcXVpdGUgYSBiaXQuIFRoYXQncyBwcm9iYWJseSBhIGJhZCB0aGluZy5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfE9iamVjdHxSZWdFeHB9IGV2dCBBbiBldmVudCBuYW1lIGlmIHlvdSB3aWxsIHBhc3MgYW4gYXJyYXkgb2YgbGlzdGVuZXJzIG5leHQuIEFuIG9iamVjdCBpZiB5b3Ugd2lzaCB0byBhZGQgdG8gbXVsdGlwbGUgZXZlbnRzIGF0IG9uY2UuXG4gICAgICogQHBhcmFtIHtGdW5jdGlvbltdfSBbbGlzdGVuZXJzXSBBbiBvcHRpb25hbCBhcnJheSBvZiBsaXN0ZW5lciBmdW5jdGlvbnMgdG8gYWRkLlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQ3VycmVudCBpbnN0YW5jZSBvZiBFdmVudEVtaXR0ZXIgZm9yIGNoYWluaW5nLlxuICAgICAqL1xuICAgIHByb3RvLmFkZExpc3RlbmVycyA9IGZ1bmN0aW9uIGFkZExpc3RlbmVycyhldnQsIGxpc3RlbmVycykge1xuICAgICAgICAvLyBQYXNzIHRocm91Z2ggdG8gbWFuaXB1bGF0ZUxpc3RlbmVyc1xuICAgICAgICByZXR1cm4gdGhpcy5tYW5pcHVsYXRlTGlzdGVuZXJzKGZhbHNlLCBldnQsIGxpc3RlbmVycyk7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIFJlbW92ZXMgbGlzdGVuZXJzIGluIGJ1bGsgdXNpbmcgdGhlIG1hbmlwdWxhdGVMaXN0ZW5lcnMgbWV0aG9kLlxuICAgICAqIElmIHlvdSBwYXNzIGFuIG9iamVjdCBhcyB0aGUgc2Vjb25kIGFyZ3VtZW50IHlvdSBjYW4gcmVtb3ZlIGZyb20gbXVsdGlwbGUgZXZlbnRzIGF0IG9uY2UuIFRoZSBvYmplY3Qgc2hvdWxkIGNvbnRhaW4ga2V5IHZhbHVlIHBhaXJzIG9mIGV2ZW50cyBhbmQgbGlzdGVuZXJzIG9yIGxpc3RlbmVyIGFycmF5cy5cbiAgICAgKiBZb3UgY2FuIGFsc28gcGFzcyBpdCBhbiBldmVudCBuYW1lIGFuZCBhbiBhcnJheSBvZiBsaXN0ZW5lcnMgdG8gYmUgcmVtb3ZlZC5cbiAgICAgKiBZb3UgY2FuIGFsc28gcGFzcyBpdCBhIHJlZ3VsYXIgZXhwcmVzc2lvbiB0byByZW1vdmUgdGhlIGxpc3RlbmVycyBmcm9tIGFsbCBldmVudHMgdGhhdCBtYXRjaCBpdC5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfE9iamVjdHxSZWdFeHB9IGV2dCBBbiBldmVudCBuYW1lIGlmIHlvdSB3aWxsIHBhc3MgYW4gYXJyYXkgb2YgbGlzdGVuZXJzIG5leHQuIEFuIG9iamVjdCBpZiB5b3Ugd2lzaCB0byByZW1vdmUgZnJvbSBtdWx0aXBsZSBldmVudHMgYXQgb25jZS5cbiAgICAgKiBAcGFyYW0ge0Z1bmN0aW9uW119IFtsaXN0ZW5lcnNdIEFuIG9wdGlvbmFsIGFycmF5IG9mIGxpc3RlbmVyIGZ1bmN0aW9ucyB0byByZW1vdmUuXG4gICAgICogQHJldHVybiB7T2JqZWN0fSBDdXJyZW50IGluc3RhbmNlIG9mIEV2ZW50RW1pdHRlciBmb3IgY2hhaW5pbmcuXG4gICAgICovXG4gICAgcHJvdG8ucmVtb3ZlTGlzdGVuZXJzID0gZnVuY3Rpb24gcmVtb3ZlTGlzdGVuZXJzKGV2dCwgbGlzdGVuZXJzKSB7XG4gICAgICAgIC8vIFBhc3MgdGhyb3VnaCB0byBtYW5pcHVsYXRlTGlzdGVuZXJzXG4gICAgICAgIHJldHVybiB0aGlzLm1hbmlwdWxhdGVMaXN0ZW5lcnModHJ1ZSwgZXZ0LCBsaXN0ZW5lcnMpO1xuICAgIH07XG5cbiAgICAvKipcbiAgICAgKiBFZGl0cyBsaXN0ZW5lcnMgaW4gYnVsay4gVGhlIGFkZExpc3RlbmVycyBhbmQgcmVtb3ZlTGlzdGVuZXJzIG1ldGhvZHMgYm90aCB1c2UgdGhpcyB0byBkbyB0aGVpciBqb2IuIFlvdSBzaG91bGQgcmVhbGx5IHVzZSB0aG9zZSBpbnN0ZWFkLCB0aGlzIGlzIGEgbGl0dGxlIGxvd2VyIGxldmVsLlxuICAgICAqIFRoZSBmaXJzdCBhcmd1bWVudCB3aWxsIGRldGVybWluZSBpZiB0aGUgbGlzdGVuZXJzIGFyZSByZW1vdmVkICh0cnVlKSBvciBhZGRlZCAoZmFsc2UpLlxuICAgICAqIElmIHlvdSBwYXNzIGFuIG9iamVjdCBhcyB0aGUgc2Vjb25kIGFyZ3VtZW50IHlvdSBjYW4gYWRkL3JlbW92ZSBmcm9tIG11bHRpcGxlIGV2ZW50cyBhdCBvbmNlLiBUaGUgb2JqZWN0IHNob3VsZCBjb250YWluIGtleSB2YWx1ZSBwYWlycyBvZiBldmVudHMgYW5kIGxpc3RlbmVycyBvciBsaXN0ZW5lciBhcnJheXMuXG4gICAgICogWW91IGNhbiBhbHNvIHBhc3MgaXQgYW4gZXZlbnQgbmFtZSBhbmQgYW4gYXJyYXkgb2YgbGlzdGVuZXJzIHRvIGJlIGFkZGVkL3JlbW92ZWQuXG4gICAgICogWW91IGNhbiBhbHNvIHBhc3MgaXQgYSByZWd1bGFyIGV4cHJlc3Npb24gdG8gbWFuaXB1bGF0ZSB0aGUgbGlzdGVuZXJzIG9mIGFsbCBldmVudHMgdGhhdCBtYXRjaCBpdC5cbiAgICAgKlxuICAgICAqIEBwYXJhbSB7Qm9vbGVhbn0gcmVtb3ZlIFRydWUgaWYgeW91IHdhbnQgdG8gcmVtb3ZlIGxpc3RlbmVycywgZmFsc2UgaWYgeW91IHdhbnQgdG8gYWRkLlxuICAgICAqIEBwYXJhbSB7U3RyaW5nfE9iamVjdHxSZWdFeHB9IGV2dCBBbiBldmVudCBuYW1lIGlmIHlvdSB3aWxsIHBhc3MgYW4gYXJyYXkgb2YgbGlzdGVuZXJzIG5leHQuIEFuIG9iamVjdCBpZiB5b3Ugd2lzaCB0byBhZGQvcmVtb3ZlIGZyb20gbXVsdGlwbGUgZXZlbnRzIGF0IG9uY2UuXG4gICAgICogQHBhcmFtIHtGdW5jdGlvbltdfSBbbGlzdGVuZXJzXSBBbiBvcHRpb25hbCBhcnJheSBvZiBsaXN0ZW5lciBmdW5jdGlvbnMgdG8gYWRkL3JlbW92ZS5cbiAgICAgKiBAcmV0dXJuIHtPYmplY3R9IEN1cnJlbnQgaW5zdGFuY2Ugb2YgRXZlbnRFbWl0dGVyIGZvciBjaGFpbmluZy5cbiAgICAgKi9cbiAgICBwcm90by5tYW5pcHVsYXRlTGlzdGVuZXJzID0gZnVuY3Rpb24gbWFuaXB1bGF0ZUxpc3RlbmVycyhyZW1vdmUsIGV2dCwgbGlzdGVuZXJzKSB7XG4gICAgICAgIHZhciBpO1xuICAgICAgICB2YXIgdmFsdWU7XG4gICAgICAgIHZhciBzaW5nbGUgPSByZW1vdmUgPyB0aGlzLnJlbW92ZUxpc3RlbmVyIDogdGhpcy5hZGRMaXN0ZW5lcjtcbiAgICAgICAgdmFyIG11bHRpcGxlID0gcmVtb3ZlID8gdGhpcy5yZW1vdmVMaXN0ZW5lcnMgOiB0aGlzLmFkZExpc3RlbmVycztcblxuICAgICAgICAvLyBJZiBldnQgaXMgYW4gb2JqZWN0IHRoZW4gcGFzcyBlYWNoIG9mIGl0cyBwcm9wZXJ0aWVzIHRvIHRoaXMgbWV0aG9kXG4gICAgICAgIGlmICh0eXBlb2YgZXZ0ID09PSAnb2JqZWN0JyAmJiAhKGV2dCBpbnN0YW5jZW9mIFJlZ0V4cCkpIHtcbiAgICAgICAgICAgIGZvciAoaSBpbiBldnQpIHtcbiAgICAgICAgICAgICAgICBpZiAoZXZ0Lmhhc093blByb3BlcnR5KGkpICYmICh2YWx1ZSA9IGV2dFtpXSkpIHtcbiAgICAgICAgICAgICAgICAgICAgLy8gUGFzcyB0aGUgc2luZ2xlIGxpc3RlbmVyIHN0cmFpZ2h0IHRocm91Z2ggdG8gdGhlIHNpbmd1bGFyIG1ldGhvZFxuICAgICAgICAgICAgICAgICAgICBpZiAodHlwZW9mIHZhbHVlID09PSAnZnVuY3Rpb24nKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBzaW5nbGUuY2FsbCh0aGlzLCBpLCB2YWx1ZSk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAvLyBPdGhlcndpc2UgcGFzcyBiYWNrIHRvIHRoZSBtdWx0aXBsZSBmdW5jdGlvblxuICAgICAgICAgICAgICAgICAgICAgICAgbXVsdGlwbGUuY2FsbCh0aGlzLCBpLCB2YWx1ZSk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgZWxzZSB7XG4gICAgICAgICAgICAvLyBTbyBldnQgbXVzdCBiZSBhIHN0cmluZ1xuICAgICAgICAgICAgLy8gQW5kIGxpc3RlbmVycyBtdXN0IGJlIGFuIGFycmF5IG9mIGxpc3RlbmVyc1xuICAgICAgICAgICAgLy8gTG9vcCBvdmVyIGl0IGFuZCBwYXNzIGVhY2ggb25lIHRvIHRoZSBtdWx0aXBsZSBtZXRob2RcbiAgICAgICAgICAgIGkgPSBsaXN0ZW5lcnMubGVuZ3RoO1xuICAgICAgICAgICAgd2hpbGUgKGktLSkge1xuICAgICAgICAgICAgICAgIHNpbmdsZS5jYWxsKHRoaXMsIGV2dCwgbGlzdGVuZXJzW2ldKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIHJldHVybiB0aGlzO1xuICAgIH07XG5cbiAgICAvKipcbiAgICAgKiBSZW1vdmVzIGFsbCBsaXN0ZW5lcnMgZnJvbSBhIHNwZWNpZmllZCBldmVudC5cbiAgICAgKiBJZiB5b3UgZG8gbm90IHNwZWNpZnkgYW4gZXZlbnQgdGhlbiBhbGwgbGlzdGVuZXJzIHdpbGwgYmUgcmVtb3ZlZC5cbiAgICAgKiBUaGF0IG1lYW5zIGV2ZXJ5IGV2ZW50IHdpbGwgYmUgZW1wdGllZC5cbiAgICAgKiBZb3UgY2FuIGFsc28gcGFzcyBhIHJlZ2V4IHRvIHJlbW92ZSBhbGwgZXZlbnRzIHRoYXQgbWF0Y2ggaXQuXG4gICAgICpcbiAgICAgKiBAcGFyYW0ge1N0cmluZ3xSZWdFeHB9IFtldnRdIE9wdGlvbmFsIG5hbWUgb2YgdGhlIGV2ZW50IHRvIHJlbW92ZSBhbGwgbGlzdGVuZXJzIGZvci4gV2lsbCByZW1vdmUgZnJvbSBldmVyeSBldmVudCBpZiBub3QgcGFzc2VkLlxuICAgICAqIEByZXR1cm4ge09iamVjdH0gQ3VycmVudCBpbnN0YW5jZSBvZiBFdmVudEVtaXR0ZXIgZm9yIGNoYWluaW5nLlxuICAgICAqL1xuICAgIHByb3RvLnJlbW92ZUV2ZW50ID0gZnVuY3Rpb24gcmVtb3ZlRXZlbnQoZXZ0KSB7XG4gICAgICAgIHZhciB0eXBlID0gdHlwZW9mIGV2dDtcbiAgICAgICAgdmFyIGV2ZW50cyA9IHRoaXMuX2dldEV2ZW50cygpO1xuICAgICAgICB2YXIga2V5O1xuXG4gICAgICAgIC8vIFJlbW92ZSBkaWZmZXJlbnQgdGhpbmdzIGRlcGVuZGluZyBvbiB0aGUgc3RhdGUgb2YgZXZ0XG4gICAgICAgIGlmICh0eXBlID09PSAnc3RyaW5nJykge1xuICAgICAgICAgICAgLy8gUmVtb3ZlIGFsbCBsaXN0ZW5lcnMgZm9yIHRoZSBzcGVjaWZpZWQgZXZlbnRcbiAgICAgICAgICAgIGRlbGV0ZSBldmVudHNbZXZ0XTtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIGlmIChldnQgaW5zdGFuY2VvZiBSZWdFeHApIHtcbiAgICAgICAgICAgIC8vIFJlbW92ZSBhbGwgZXZlbnRzIG1hdGNoaW5nIHRoZSByZWdleC5cbiAgICAgICAgICAgIGZvciAoa2V5IGluIGV2ZW50cykge1xuICAgICAgICAgICAgICAgIGlmIChldmVudHMuaGFzT3duUHJvcGVydHkoa2V5KSAmJiBldnQudGVzdChrZXkpKSB7XG4gICAgICAgICAgICAgICAgICAgIGRlbGV0ZSBldmVudHNba2V5XTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgZWxzZSB7XG4gICAgICAgICAgICAvLyBSZW1vdmUgYWxsIGxpc3RlbmVycyBpbiBhbGwgZXZlbnRzXG4gICAgICAgICAgICBkZWxldGUgdGhpcy5fZXZlbnRzO1xuICAgICAgICB9XG5cbiAgICAgICAgcmV0dXJuIHRoaXM7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIEFsaWFzIG9mIHJlbW92ZUV2ZW50LlxuICAgICAqXG4gICAgICogQWRkZWQgdG8gbWlycm9yIHRoZSBub2RlIEFQSS5cbiAgICAgKi9cbiAgICBwcm90by5yZW1vdmVBbGxMaXN0ZW5lcnMgPSBhbGlhcygncmVtb3ZlRXZlbnQnKTtcblxuICAgIC8qKlxuICAgICAqIEVtaXRzIGFuIGV2ZW50IG9mIHlvdXIgY2hvaWNlLlxuICAgICAqIFdoZW4gZW1pdHRlZCwgZXZlcnkgbGlzdGVuZXIgYXR0YWNoZWQgdG8gdGhhdCBldmVudCB3aWxsIGJlIGV4ZWN1dGVkLlxuICAgICAqIElmIHlvdSBwYXNzIHRoZSBvcHRpb25hbCBhcmd1bWVudCBhcnJheSB0aGVuIHRob3NlIGFyZ3VtZW50cyB3aWxsIGJlIHBhc3NlZCB0byBldmVyeSBsaXN0ZW5lciB1cG9uIGV4ZWN1dGlvbi5cbiAgICAgKiBCZWNhdXNlIGl0IHVzZXMgYGFwcGx5YCwgeW91ciBhcnJheSBvZiBhcmd1bWVudHMgd2lsbCBiZSBwYXNzZWQgYXMgaWYgeW91IHdyb3RlIHRoZW0gb3V0IHNlcGFyYXRlbHkuXG4gICAgICogU28gdGhleSB3aWxsIG5vdCBhcnJpdmUgd2l0aGluIHRoZSBhcnJheSBvbiB0aGUgb3RoZXIgc2lkZSwgdGhleSB3aWxsIGJlIHNlcGFyYXRlLlxuICAgICAqIFlvdSBjYW4gYWxzbyBwYXNzIGEgcmVndWxhciBleHByZXNzaW9uIHRvIGVtaXQgdG8gYWxsIGV2ZW50cyB0aGF0IG1hdGNoIGl0LlxuICAgICAqXG4gICAgICogQHBhcmFtIHtTdHJpbmd8UmVnRXhwfSBldnQgTmFtZSBvZiB0aGUgZXZlbnQgdG8gZW1pdCBhbmQgZXhlY3V0ZSBsaXN0ZW5lcnMgZm9yLlxuICAgICAqIEBwYXJhbSB7QXJyYXl9IFthcmdzXSBPcHRpb25hbCBhcnJheSBvZiBhcmd1bWVudHMgdG8gYmUgcGFzc2VkIHRvIGVhY2ggbGlzdGVuZXIuXG4gICAgICogQHJldHVybiB7T2JqZWN0fSBDdXJyZW50IGluc3RhbmNlIG9mIEV2ZW50RW1pdHRlciBmb3IgY2hhaW5pbmcuXG4gICAgICovXG4gICAgcHJvdG8uZW1pdEV2ZW50ID0gZnVuY3Rpb24gZW1pdEV2ZW50KGV2dCwgYXJncykge1xuICAgICAgICB2YXIgbGlzdGVuZXJzTWFwID0gdGhpcy5nZXRMaXN0ZW5lcnNBc09iamVjdChldnQpO1xuICAgICAgICB2YXIgbGlzdGVuZXJzO1xuICAgICAgICB2YXIgbGlzdGVuZXI7XG4gICAgICAgIHZhciBpO1xuICAgICAgICB2YXIga2V5O1xuICAgICAgICB2YXIgcmVzcG9uc2U7XG5cbiAgICAgICAgZm9yIChrZXkgaW4gbGlzdGVuZXJzTWFwKSB7XG4gICAgICAgICAgICBpZiAobGlzdGVuZXJzTWFwLmhhc093blByb3BlcnR5KGtleSkpIHtcbiAgICAgICAgICAgICAgICBsaXN0ZW5lcnMgPSBsaXN0ZW5lcnNNYXBba2V5XS5zbGljZSgwKTtcblxuICAgICAgICAgICAgICAgIGZvciAoaSA9IDA7IGkgPCBsaXN0ZW5lcnMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgICAgICAgICAgICAgLy8gSWYgdGhlIGxpc3RlbmVyIHJldHVybnMgdHJ1ZSB0aGVuIGl0IHNoYWxsIGJlIHJlbW92ZWQgZnJvbSB0aGUgZXZlbnRcbiAgICAgICAgICAgICAgICAgICAgLy8gVGhlIGZ1bmN0aW9uIGlzIGV4ZWN1dGVkIGVpdGhlciB3aXRoIGEgYmFzaWMgY2FsbCBvciBhbiBhcHBseSBpZiB0aGVyZSBpcyBhbiBhcmdzIGFycmF5XG4gICAgICAgICAgICAgICAgICAgIGxpc3RlbmVyID0gbGlzdGVuZXJzW2ldO1xuXG4gICAgICAgICAgICAgICAgICAgIGlmIChsaXN0ZW5lci5vbmNlID09PSB0cnVlKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnJlbW92ZUxpc3RlbmVyKGV2dCwgbGlzdGVuZXIubGlzdGVuZXIpO1xuICAgICAgICAgICAgICAgICAgICB9XG5cbiAgICAgICAgICAgICAgICAgICAgcmVzcG9uc2UgPSBsaXN0ZW5lci5saXN0ZW5lci5hcHBseSh0aGlzLCBhcmdzIHx8IFtdKTtcblxuICAgICAgICAgICAgICAgICAgICBpZiAocmVzcG9uc2UgPT09IHRoaXMuX2dldE9uY2VSZXR1cm5WYWx1ZSgpKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnJlbW92ZUxpc3RlbmVyKGV2dCwgbGlzdGVuZXIubGlzdGVuZXIpO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9XG5cbiAgICAgICAgcmV0dXJuIHRoaXM7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIEFsaWFzIG9mIGVtaXRFdmVudFxuICAgICAqL1xuICAgIHByb3RvLnRyaWdnZXIgPSBhbGlhcygnZW1pdEV2ZW50Jyk7XG5cbiAgICAvKipcbiAgICAgKiBTdWJ0bHkgZGlmZmVyZW50IGZyb20gZW1pdEV2ZW50IGluIHRoYXQgaXQgd2lsbCBwYXNzIGl0cyBhcmd1bWVudHMgb24gdG8gdGhlIGxpc3RlbmVycywgYXMgb3Bwb3NlZCB0byB0YWtpbmcgYSBzaW5nbGUgYXJyYXkgb2YgYXJndW1lbnRzIHRvIHBhc3Mgb24uXG4gICAgICogQXMgd2l0aCBlbWl0RXZlbnQsIHlvdSBjYW4gcGFzcyBhIHJlZ2V4IGluIHBsYWNlIG9mIHRoZSBldmVudCBuYW1lIHRvIGVtaXQgdG8gYWxsIGV2ZW50cyB0aGF0IG1hdGNoIGl0LlxuICAgICAqXG4gICAgICogQHBhcmFtIHtTdHJpbmd8UmVnRXhwfSBldnQgTmFtZSBvZiB0aGUgZXZlbnQgdG8gZW1pdCBhbmQgZXhlY3V0ZSBsaXN0ZW5lcnMgZm9yLlxuICAgICAqIEBwYXJhbSB7Li4uKn0gT3B0aW9uYWwgYWRkaXRpb25hbCBhcmd1bWVudHMgdG8gYmUgcGFzc2VkIHRvIGVhY2ggbGlzdGVuZXIuXG4gICAgICogQHJldHVybiB7T2JqZWN0fSBDdXJyZW50IGluc3RhbmNlIG9mIEV2ZW50RW1pdHRlciBmb3IgY2hhaW5pbmcuXG4gICAgICovXG4gICAgcHJvdG8uZW1pdCA9IGZ1bmN0aW9uIGVtaXQoZXZ0KSB7XG4gICAgICAgIHZhciBhcmdzID0gQXJyYXkucHJvdG90eXBlLnNsaWNlLmNhbGwoYXJndW1lbnRzLCAxKTtcbiAgICAgICAgcmV0dXJuIHRoaXMuZW1pdEV2ZW50KGV2dCwgYXJncyk7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIFNldHMgdGhlIGN1cnJlbnQgdmFsdWUgdG8gY2hlY2sgYWdhaW5zdCB3aGVuIGV4ZWN1dGluZyBsaXN0ZW5lcnMuIElmIGFcbiAgICAgKiBsaXN0ZW5lcnMgcmV0dXJuIHZhbHVlIG1hdGNoZXMgdGhlIG9uZSBzZXQgaGVyZSB0aGVuIGl0IHdpbGwgYmUgcmVtb3ZlZFxuICAgICAqIGFmdGVyIGV4ZWN1dGlvbi4gVGhpcyB2YWx1ZSBkZWZhdWx0cyB0byB0cnVlLlxuICAgICAqXG4gICAgICogQHBhcmFtIHsqfSB2YWx1ZSBUaGUgbmV3IHZhbHVlIHRvIGNoZWNrIGZvciB3aGVuIGV4ZWN1dGluZyBsaXN0ZW5lcnMuXG4gICAgICogQHJldHVybiB7T2JqZWN0fSBDdXJyZW50IGluc3RhbmNlIG9mIEV2ZW50RW1pdHRlciBmb3IgY2hhaW5pbmcuXG4gICAgICovXG4gICAgcHJvdG8uc2V0T25jZVJldHVyblZhbHVlID0gZnVuY3Rpb24gc2V0T25jZVJldHVyblZhbHVlKHZhbHVlKSB7XG4gICAgICAgIHRoaXMuX29uY2VSZXR1cm5WYWx1ZSA9IHZhbHVlO1xuICAgICAgICByZXR1cm4gdGhpcztcbiAgICB9O1xuXG4gICAgLyoqXG4gICAgICogRmV0Y2hlcyB0aGUgY3VycmVudCB2YWx1ZSB0byBjaGVjayBhZ2FpbnN0IHdoZW4gZXhlY3V0aW5nIGxpc3RlbmVycy4gSWZcbiAgICAgKiB0aGUgbGlzdGVuZXJzIHJldHVybiB2YWx1ZSBtYXRjaGVzIHRoaXMgb25lIHRoZW4gaXQgc2hvdWxkIGJlIHJlbW92ZWRcbiAgICAgKiBhdXRvbWF0aWNhbGx5LiBJdCB3aWxsIHJldHVybiB0cnVlIGJ5IGRlZmF1bHQuXG4gICAgICpcbiAgICAgKiBAcmV0dXJuIHsqfEJvb2xlYW59IFRoZSBjdXJyZW50IHZhbHVlIHRvIGNoZWNrIGZvciBvciB0aGUgZGVmYXVsdCwgdHJ1ZS5cbiAgICAgKiBAYXBpIHByaXZhdGVcbiAgICAgKi9cbiAgICBwcm90by5fZ2V0T25jZVJldHVyblZhbHVlID0gZnVuY3Rpb24gX2dldE9uY2VSZXR1cm5WYWx1ZSgpIHtcbiAgICAgICAgaWYgKHRoaXMuaGFzT3duUHJvcGVydHkoJ19vbmNlUmV0dXJuVmFsdWUnKSkge1xuICAgICAgICAgICAgcmV0dXJuIHRoaXMuX29uY2VSZXR1cm5WYWx1ZTtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIHtcbiAgICAgICAgICAgIHJldHVybiB0cnVlO1xuICAgICAgICB9XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIEZldGNoZXMgdGhlIGV2ZW50cyBvYmplY3QgYW5kIGNyZWF0ZXMgb25lIGlmIHJlcXVpcmVkLlxuICAgICAqXG4gICAgICogQHJldHVybiB7T2JqZWN0fSBUaGUgZXZlbnRzIHN0b3JhZ2Ugb2JqZWN0LlxuICAgICAqIEBhcGkgcHJpdmF0ZVxuICAgICAqL1xuICAgIHByb3RvLl9nZXRFdmVudHMgPSBmdW5jdGlvbiBfZ2V0RXZlbnRzKCkge1xuICAgICAgICByZXR1cm4gdGhpcy5fZXZlbnRzIHx8ICh0aGlzLl9ldmVudHMgPSB7fSk7XG4gICAgfTtcblxuICAgIC8qKlxuICAgICAqIFJldmVydHMgdGhlIGdsb2JhbCB7QGxpbmsgRXZlbnRFbWl0dGVyfSB0byBpdHMgcHJldmlvdXMgdmFsdWUgYW5kIHJldHVybnMgYSByZWZlcmVuY2UgdG8gdGhpcyB2ZXJzaW9uLlxuICAgICAqXG4gICAgICogQHJldHVybiB7RnVuY3Rpb259IE5vbiBjb25mbGljdGluZyBFdmVudEVtaXR0ZXIgY2xhc3MuXG4gICAgICovXG4gICAgRXZlbnRFbWl0dGVyLm5vQ29uZmxpY3QgPSBmdW5jdGlvbiBub0NvbmZsaWN0KCkge1xuICAgICAgICBleHBvcnRzLkV2ZW50RW1pdHRlciA9IG9yaWdpbmFsR2xvYmFsVmFsdWU7XG4gICAgICAgIHJldHVybiBFdmVudEVtaXR0ZXI7XG4gICAgfTtcblxuICAgIC8vIEV4cG9zZSB0aGUgY2xhc3MgZWl0aGVyIHZpYSBBTUQsIENvbW1vbkpTIG9yIHRoZSBnbG9iYWwgb2JqZWN0XG4gICAgaWYgKHR5cGVvZiBkZWZpbmUgPT09ICdmdW5jdGlvbicgJiYgZGVmaW5lLmFtZCkge1xuICAgICAgICBkZWZpbmUoZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgcmV0dXJuIEV2ZW50RW1pdHRlcjtcbiAgICAgICAgfSk7XG4gICAgfVxuICAgIGVsc2UgaWYgKHR5cGVvZiBtb2R1bGUgPT09ICdvYmplY3QnICYmIG1vZHVsZS5leHBvcnRzKXtcbiAgICAgICAgbW9kdWxlLmV4cG9ydHMgPSBFdmVudEVtaXR0ZXI7XG4gICAgfVxuICAgIGVsc2Uge1xuICAgICAgICBleHBvcnRzLkV2ZW50RW1pdHRlciA9IEV2ZW50RW1pdHRlcjtcbiAgICB9XG59KHRoaXMgfHwge30pKTtcbiIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyLCBBbmltYXRpb25TZXR0aW5ncyB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBCYXNlQ2FudmFzIGZyb20gJy4vQmFzZUNhbnZhcyc7XG5pbXBvcnQgeyBtZXJnZU9wdGlvbnMsIGVhc2VGdW5jdGlvbnMgfSBmcm9tICcuLi91dGlscyc7XG5cbnR5cGUgVGltZWxpbmUgPSB7XG4gICAgYWN0aXZlOiBib29sZWFuO1xuICAgIGluaXRpYWxpemVkOiBib29sZWFuO1xuICAgIGNvbXBsZXRlZDogYm9vbGVhbjtcbiAgICBzdGFydFZhbHVlOiBhbnk7XG4gICAgYnlWYWx1ZTogYW55O1xuICAgIGVuZFZhbHVlOiBhbnk7XG4gICAgZWFzZT86IEZ1bmN0aW9uO1xuICAgIG9uQ29tcGxldGU/OiBGdW5jdGlvbjtcbiAgICBrZXlQb2ludDogbnVtYmVyO1xuICAgIGR1cmF0aW9uOiBudW1iZXI7XG4gICAgYmVnaW5UaW1lOiBudW1iZXI7XG4gICAgZW5kVGltZTogbnVtYmVyO1xuICAgIGZyb20/OiBhbnk7XG4gICAgdG86IGFueTtcbn1cblxuY2xhc3MgQW5pbWF0aW9uIHtcbiAgICBfcGxheWVyOiBQbGF5ZXI7XG4gICAgX29wdGlvbnM6IHtcbiAgICAgICAgYW5pbWF0aW9uOiBBbmltYXRpb25TZXR0aW5nc1tdO1xuICAgICAgICBjYW52YXM6IEJhc2VDYW52YXNcbiAgICB9O1xuICAgIF9jYW52YXM6IEJhc2VDYW52YXM7XG4gICAgX3RpbWVsaW5lOiBUaW1lbGluZVtdO1xuICAgIF9hY3RpdmU6IGJvb2xlYW47XG5cbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczoge2FuaW1hdGlvbjogQW5pbWF0aW9uU2V0dGluZ3NbXSwgY2FudmFzOiBCYXNlQ2FudmFzfSl7XG4gICAgICAgIHRoaXMuX3BsYXllciA9IHBsYXllcjtcbiAgICAgICAgdGhpcy5fb3B0aW9ucyA9IG1lcmdlT3B0aW9ucyh7fSwgdGhpcy5fb3B0aW9ucyk7XG4gICAgICAgIHRoaXMuX29wdGlvbnMgPSBtZXJnZU9wdGlvbnModGhpcy5fb3B0aW9ucywgb3B0aW9ucyk7XG5cbiAgICAgICAgdGhpcy5fY2FudmFzID0gdGhpcy5fb3B0aW9ucy5jYW52YXM7XG4gICAgICAgIHRoaXMuX3RpbWVsaW5lID0gW107XG5cbiAgICAgICAgdGhpcy5fb3B0aW9ucy5hbmltYXRpb24uZm9yRWFjaCgob2JqOiBBbmltYXRpb25TZXR0aW5ncykgPT57XG4gICAgICAgICAgICB0aGlzLmFkZFRpbWVsaW5lKG9iaik7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIGFkZFRpbWVsaW5lKG9wdDogQW5pbWF0aW9uU2V0dGluZ3Mpe1xuICAgICAgICBsZXQgdGltZWxpbmU6IFRpbWVsaW5lID0ge1xuICAgICAgICAgICAgYWN0aXZlOiBmYWxzZSxcbiAgICAgICAgICAgIGluaXRpYWxpemVkOiBmYWxzZSxcbiAgICAgICAgICAgIGNvbXBsZXRlZDogZmFsc2UsXG4gICAgICAgICAgICBzdGFydFZhbHVlOiB7fSxcbiAgICAgICAgICAgIGJ5VmFsdWU6IHt9LFxuICAgICAgICAgICAgZW5kVmFsdWU6IHt9LFxuICAgICAgICAgICAga2V5UG9pbnQ6IG9wdC5rZXlQb2ludCxcbiAgICAgICAgICAgIGR1cmF0aW9uOiBvcHQuZHVyYXRpb24sXG4gICAgICAgICAgICBiZWdpblRpbWU6IEluZmluaXR5LFxuICAgICAgICAgICAgZW5kVGltZTogSW5maW5pdHksXG4gICAgICAgICAgICBvbkNvbXBsZXRlOiBvcHQub25Db21wbGV0ZSxcbiAgICAgICAgICAgIGZyb206IG9wdC5mcm9tLFxuICAgICAgICAgICAgdG86IG9wdC50b1xuICAgICAgICB9O1xuXG4gICAgICAgIGlmKHR5cGVvZiBvcHQuZWFzZSA9PT0gXCJzdHJpbmdcIil7XG4gICAgICAgICAgICB0aW1lbGluZS5lYXNlID0gZWFzZUZ1bmN0aW9uc1tvcHQuZWFzZV07XG4gICAgICAgIH1cbiAgICAgICAgaWYodHlwZW9mIG9wdC5lYXNlID09PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHRpbWVsaW5lLmVhc2UgPSBlYXNlRnVuY3Rpb25zLmxpbmVhcjtcbiAgICAgICAgfVxuXG4gICAgICAgIHRoaXMuX3RpbWVsaW5lLnB1c2godGltZWxpbmUpO1xuICAgICAgICB0aGlzLmF0dGFjaEV2ZW50cygpO1xuICAgIH1cblxuICAgIGluaXRpYWxUaW1lbGluZSh0aW1lbGluZTogVGltZWxpbmUpe1xuICAgICAgICBmb3IobGV0IGtleSBpbiB0aW1lbGluZS50byl7XG4gICAgICAgICAgICBpZih0aW1lbGluZS50by5oYXNPd25Qcm9wZXJ0eShrZXkpKXtcbiAgICAgICAgICAgICAgICBsZXQgZnJvbSA9IHRpbWVsaW5lLmZyb20/ICh0eXBlb2YgdGltZWxpbmUuZnJvbVtrZXldICE9PSBcInVuZGVmaW5lZFwiPyB0aW1lbGluZS5mcm9tW2tleV0gOiB0aGlzLl9jYW52YXNbYF8ke2tleX1gXSkgOiB0aGlzLl9jYW52YXNbYF8ke2tleX1gXTtcbiAgICAgICAgICAgICAgICB0aW1lbGluZS5zdGFydFZhbHVlW2tleV0gPSBmcm9tO1xuICAgICAgICAgICAgICAgIHRpbWVsaW5lLmVuZFZhbHVlW2tleV0gPSB0aW1lbGluZS50b1trZXldO1xuICAgICAgICAgICAgICAgIHRpbWVsaW5lLmJ5VmFsdWVba2V5XSAgPSB0aW1lbGluZS50b1trZXldIC0gZnJvbTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cblxuICAgIHByb2Nlc3NUaW1lbGluZSh0aW1lbGluZTogVGltZWxpbmUsIGFuaW1hdGlvblRpbWU6IG51bWJlcil7XG4gICAgICAgIGZvciAobGV0IGtleSBpbiB0aW1lbGluZS50byl7XG4gICAgICAgICAgICBpZiAodGltZWxpbmUudG8uaGFzT3duUHJvcGVydHkoa2V5KSkge1xuICAgICAgICAgICAgICAgIGxldCBuZXdWYWwgPSB0aW1lbGluZS5lYXNlICYmIHRpbWVsaW5lLmVhc2UoYW5pbWF0aW9uVGltZSwgdGltZWxpbmUuc3RhcnRWYWx1ZVtrZXldLCB0aW1lbGluZS5ieVZhbHVlW2tleV0sIHRpbWVsaW5lLmR1cmF0aW9uKTtcbiAgICAgICAgICAgICAgICBpZihrZXkgPT09IFwiZm92XCIpe1xuICAgICAgICAgICAgICAgICAgICB0aGlzLl9jYW52YXMuX2NhbWVyYS5mb3YgPSBuZXdWYWw7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuX2NhbnZhcy5fY2FtZXJhLnVwZGF0ZVByb2plY3Rpb25NYXRyaXgoKTtcbiAgICAgICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICAgICAgdGhpcy5fY2FudmFzW2BfJHtrZXl9YF0gPSBuZXdWYWw7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxuXG4gICAgYXR0YWNoRXZlbnRzKCl7XG4gICAgICAgIHRoaXMuX2FjdGl2ZSA9IHRydWU7XG4gICAgICAgIHRoaXMuX2NhbnZhcy5hZGRMaXN0ZW5lcihcImJlZm9yZVJlbmRlclwiLCB0aGlzLnJlbmRlckFuaW1hdGlvbi5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5fcGxheWVyLm9uKFwic2Vla2VkXCIsIHRoaXMuaGFuZGxlVmlkZW9TZWVrLmJpbmQodGhpcykpO1xuICAgIH1cblxuICAgIGRldGFjaEV2ZW50cygpe1xuICAgICAgICB0aGlzLl9hY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgdGhpcy5fY2FudmFzLmNvbnRyb2xhYmxlID0gdHJ1ZTtcbiAgICAgICAgdGhpcy5fY2FudmFzLnJlbW92ZUxpc3RlbmVyKFwiYmVmb3JlUmVuZGVyXCIsIHRoaXMucmVuZGVyQW5pbWF0aW9uLmJpbmQodGhpcykpO1xuICAgIH1cblxuICAgIGhhbmRsZVZpZGVvU2Vlaygpe1xuICAgICAgICBsZXQgY3VycmVudFRpbWUgPSB0aGlzLl9wbGF5ZXIuZ2V0VmlkZW9FbCgpLmN1cnJlbnRUaW1lICogMTAwMDtcbiAgICAgICAgbGV0IHJlc2V0VGltZWxpbmUgPSAwO1xuICAgICAgICB0aGlzLl90aW1lbGluZS5mb3JFYWNoKCh0aW1lbGluZTogVGltZWxpbmUpPT57XG4gICAgICAgICAgICBsZXQgcmVzID0gdGltZWxpbmUua2V5UG9pbnQgPj0gY3VycmVudFRpbWUgfHwgKHRpbWVsaW5lLmtleVBvaW50IDw9IGN1cnJlbnRUaW1lICYmICh0aW1lbGluZS5rZXlQb2ludCArIHRpbWVsaW5lLmR1cmF0aW9uKSA+PSBjdXJyZW50VGltZSk7XG4gICAgICAgICAgICBpZihyZXMpe1xuICAgICAgICAgICAgICAgIHJlc2V0VGltZWxpbmUrKztcbiAgICAgICAgICAgICAgICB0aW1lbGluZS5jb21wbGV0ZWQgPSBmYWxzZTtcbiAgICAgICAgICAgICAgICB0aW1lbGluZS5pbml0aWFsaXplZCA9IGZhbHNlO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZihyZXNldFRpbWVsaW5lID4gMCAmJiAhdGhpcy5fYWN0aXZlKXtcbiAgICAgICAgICAgIHRoaXMuYXR0YWNoRXZlbnRzKCk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICByZW5kZXJBbmltYXRpb24oKXtcbiAgICAgICAgbGV0IGN1cnJlbnRUaW1lID0gdGhpcy5fcGxheWVyLmdldFZpZGVvRWwoKS5jdXJyZW50VGltZSAqIDEwMDA7XG4gICAgICAgIGxldCBjb21wbGV0ZVRpbWVsaW5lID0gMDtcbiAgICAgICAgbGV0IGluQWN0aXZlVGltZWxpbmUgPSAwO1xuICAgICAgICB0aGlzLl90aW1lbGluZS5maWx0ZXIoKHRpbWVsaW5lOiBUaW1lbGluZSk9PntcbiAgICAgICAgICAgIGlmKHRpbWVsaW5lLmNvbXBsZXRlZCkge1xuICAgICAgICAgICAgICAgIGNvbXBsZXRlVGltZWxpbmUrKztcbiAgICAgICAgICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBsZXQgcmVzID0gdGltZWxpbmUua2V5UG9pbnQgPD0gY3VycmVudFRpbWUgJiYgKHRpbWVsaW5lLmtleVBvaW50ICsgdGltZWxpbmUuZHVyYXRpb24pID4gY3VycmVudFRpbWU7XG4gICAgICAgICAgICB0aW1lbGluZS5hY3RpdmUgPSByZXM7XG4gICAgICAgICAgICBpZih0aW1lbGluZS5hY3RpdmUgPT09IGZhbHNlKSBpbkFjdGl2ZVRpbWVsaW5lKys7XG5cbiAgICAgICAgICAgIGlmKHJlcyAmJiAhdGltZWxpbmUuaW5pdGlhbGl6ZWQpe1xuICAgICAgICAgICAgICAgIHRpbWVsaW5lLmluaXRpYWxpemVkID0gdHJ1ZTtcbiAgICAgICAgICAgICAgICB0aW1lbGluZS5iZWdpblRpbWUgPSB0aW1lbGluZS5rZXlQb2ludDtcbiAgICAgICAgICAgICAgICB0aW1lbGluZS5lbmRUaW1lID0gdGltZWxpbmUuYmVnaW5UaW1lICsgdGltZWxpbmUuZHVyYXRpb247XG4gICAgICAgICAgICAgICAgdGhpcy5pbml0aWFsVGltZWxpbmUodGltZWxpbmUpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYodGltZWxpbmUuZW5kVGltZSA8PSBjdXJyZW50VGltZSl7XG4gICAgICAgICAgICAgICAgdGltZWxpbmUuY29tcGxldGVkID0gdHJ1ZTtcbiAgICAgICAgICAgICAgICB0aGlzLnByb2Nlc3NUaW1lbGluZSh0aW1lbGluZSwgdGltZWxpbmUuZHVyYXRpb24pO1xuICAgICAgICAgICAgICAgIGlmKHRpbWVsaW5lLm9uQ29tcGxldGUpe1xuICAgICAgICAgICAgICAgICAgICB0aW1lbGluZS5vbkNvbXBsZXRlLmNhbGwodGhpcyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICAgICAgcmV0dXJuIHJlcztcbiAgICAgICAgfSkuZm9yRWFjaCgodGltZWxpbmU6IFRpbWVsaW5lKT0+e1xuICAgICAgICAgICAgbGV0IGFuaW1hdGlvblRpbWUgPSBjdXJyZW50VGltZSAtIHRpbWVsaW5lLmJlZ2luVGltZTtcbiAgICAgICAgICAgIHRoaXMucHJvY2Vzc1RpbWVsaW5lKHRpbWVsaW5lLCBhbmltYXRpb25UaW1lKTtcbiAgICAgICAgfSk7XG5cbiAgICAgICAgdGhpcy5fY2FudmFzLmNvbnRyb2xhYmxlID0gaW5BY3RpdmVUaW1lbGluZSA9PT0gdGhpcy5fdGltZWxpbmUubGVuZ3RoO1xuXG4gICAgICAgIGlmKGNvbXBsZXRlVGltZWxpbmUgPT09IHRoaXMuX3RpbWVsaW5lLmxlbmd0aCl7XG4gICAgICAgICAgICB0aGlzLmRldGFjaEV2ZW50cygpO1xuICAgICAgICB9XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBBbmltYXRpb247IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIFNldHRpbmdzLCBQb2ludCwgTG9jYXRpb24gfSBmcm9tICcuLi90eXBlcyc7XG5pbXBvcnQgVEhSRUUgZnJvbSBcInRocmVlXCI7XG5pbXBvcnQgQ29tcG9uZW50IGZyb20gJy4vQ29tcG9uZW50JztcbmltcG9ydCBIZWxwZXJDYW52YXMgZnJvbSAnLi9IZWxwZXJDYW52YXMnO1xuaW1wb3J0IHsgc3VwcG9ydFZpZGVvVGV4dHVyZSwgZ2V0VG91Y2hlc0Rpc3RhbmNlLCBtb2JpbGVBbmRUYWJsZXRjaGVjayB9IGZyb20gJy4uL3V0aWxzJztcblxuY29uc3QgSEFWRV9DVVJSRU5UX0RBVEEgPSAyO1xuXG5jbGFzcyBCYXNlQ2FudmFzIGV4dGVuZHMgQ29tcG9uZW50e1xuICAgIC8qKlxuICAgICAqIERpbWVuc2lvblxuICAgICAqL1xuICAgIF93aWR0aDogbnVtYmVyO1xuICAgIF9oZWlnaHQ6IG51bWJlcjtcblxuICAgIC8qKlxuICAgICAqIFBvc2l0aW9uXG4gICAgICovXG4gICAgX2xvbjogbnVtYmVyO1xuICAgIF9sYXQ6IG51bWJlcjtcbiAgICBfcGhpOiBudW1iZXI7XG4gICAgX3RoZXRhOiBudW1iZXI7XG5cbiAgICAvKipcbiAgICAgKiBUaHJlZS5qc1xuICAgICAqL1xuICAgIF9oZWxwZXJDYW52YXM6IEhlbHBlckNhbnZhcztcbiAgICBfcmVuZGVyZXI6IGFueTtcbiAgICBfdGV4dHVyZTogYW55O1xuICAgIF9zY2VuZTogYW55O1xuXG4gICAgLyoqXG4gICAgICogSW50ZXJhY3Rpb25cbiAgICAgKi9cbiAgICBfY29udHJvbGFibGU6IGJvb2xlYW47XG4gICAgX1ZSTW9kZTogYm9vbGVhbjtcbiAgICBfbW91c2VEb3duOiBib29sZWFuO1xuICAgIF9tb3VzZURvd25Qb2ludGVyOiBQb2ludDtcbiAgICBfbW91c2VEb3duTG9jYXRpb246IExvY2F0aW9uO1xuICAgIF9hY2NlbGVjdG9yOiBQb2ludDtcblxuICAgIF9pc1VzZXJJbnRlcmFjdGluZzogYm9vbGVhbjtcbiAgICBfaXNVc2VyUGluY2g6IGJvb2xlYW47XG4gICAgX211bHRpVG91Y2hEaXN0YW5jZTogbnVtYmVyO1xuXG4gICAgX3JlcXVlc3RBbmltYXRpb25JZDogd2luZG93O1xuICAgIF90aW1lOiBudW1iZXI7XG4gICAgX3J1bk9uTW9iaWxlOiBib29sZWFuO1xuXG4gICAgLyoqXG4gICAgICogQmFzZSBjb25zdHJ1Y3RvclxuICAgICAqIEBwYXJhbSBwbGF5ZXJcbiAgICAgKiBAcGFyYW0gb3B0aW9uc1xuICAgICAqL1xuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBTZXR0aW5ncywgcmVuZGVyRWxlbWVudDogSFRNTEVsZW1lbnQpe1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMsIHJlbmRlckVsZW1lbnQpO1xuICAgICAgICB0aGlzLl93aWR0aCA9IHRoaXMucGxheWVyLmVsKCkub2Zmc2V0V2lkdGgsIHRoaXMuX2hlaWdodCA9IHRoaXMucGxheWVyLmVsKCkub2Zmc2V0SGVpZ2h0O1xuICAgICAgICB0aGlzLl9sb24gPSB0aGlzLm9wdGlvbnMuaW5pdExvbiwgdGhpcy5fbGF0ID0gdGhpcy5vcHRpb25zLmluaXRMYXQsIHRoaXMuX3BoaSA9IDAsIHRoaXMuX3RoZXRhID0gMDtcbiAgICAgICAgdGhpcy5fYWNjZWxlY3RvciA9IHtcbiAgICAgICAgICAgIHg6IDAsXG4gICAgICAgICAgICB5OiAwXG4gICAgICAgIH07XG4gICAgICAgIHRoaXMuX3JlbmRlcmVyLnNldFNpemUodGhpcy5fd2lkdGgsIHRoaXMuX2hlaWdodCk7XG5cbiAgICAgICAgLy9pbml0IGludGVyYWN0aW9uXG4gICAgICAgIHRoaXMuX21vdXNlRG93biA9IGZhbHNlO1xuICAgICAgICB0aGlzLl9pc1VzZXJJbnRlcmFjdGluZyA9IGZhbHNlO1xuICAgICAgICB0aGlzLl9ydW5Pbk1vYmlsZSA9IG1vYmlsZUFuZFRhYmxldGNoZWNrKCk7XG4gICAgICAgIHRoaXMuX1ZSTW9kZSA9IGZhbHNlO1xuICAgICAgICB0aGlzLl9jb250cm9sYWJsZSA9IHRydWU7XG5cbiAgICAgICAgdGhpcy5fbW91c2VEb3duUG9pbnRlciA9IHtcbiAgICAgICAgICAgIHg6IDAsXG4gICAgICAgICAgICB5OiAwXG4gICAgICAgIH07XG5cbiAgICAgICAgdGhpcy5fbW91c2VEb3duTG9jYXRpb24gPSB7XG4gICAgICAgICAgICBMYXQ6IDAsXG4gICAgICAgICAgICBMb246IDBcbiAgICAgICAgfTtcblxuICAgICAgICB0aGlzLmF0dGFjaENvbnRyb2xFdmVudHMoKTtcbiAgICB9XG5cblxuICAgIGNyZWF0ZUVsKHRhZ05hbWU/OiBzdHJpbmcgPSBcImRpdlwiLCBwcm9wZXJ0aWVzPzogYW55LCBhdHRyaWJ1dGVzPzogYW55KTogSFRNTEVsZW1lbnR7XG4gICAgICAgIC8qKlxuICAgICAgICAgKiBpbml0aWFsIHdlYmdsIHJlbmRlclxuICAgICAgICAgKi9cbiAgICAgICAgdGhpcy5fcmVuZGVyZXIgPSBuZXcgVEhSRUUuV2ViR0xSZW5kZXJlcigpO1xuICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRQaXhlbFJhdGlvKHdpbmRvdy5kZXZpY2VQaXhlbFJhdGlvKTtcbiAgICAgICAgdGhpcy5fcmVuZGVyZXIuYXV0b0NsZWFyID0gZmFsc2U7XG4gICAgICAgIHRoaXMuX3JlbmRlcmVyLnNldENsZWFyQ29sb3IoMHgwMDAwMDAsIDEpO1xuXG4gICAgICAgIGNvbnN0IHJlbmRlckVsZW1lbnQgPSB0aGlzLl9yZW5kZXJFbGVtZW50O1xuXG4gICAgICAgIGlmKHJlbmRlckVsZW1lbnQudGFnTmFtZS50b0xvd2VyQ2FzZSgpID09PSBcInZpZGVvXCIgJiYgKHRoaXMub3B0aW9ucy51c2VIZWxwZXJDYW52YXMgPT09IHRydWUgfHwgKCFzdXBwb3J0VmlkZW9UZXh0dXJlKHJlbmRlckVsZW1lbnQpICYmIHRoaXMub3B0aW9ucy51c2VIZWxwZXJDYW52YXMgPT09IFwiYXV0b1wiKSkpe1xuICAgICAgICAgICAgdGhpcy5faGVscGVyQ2FudmFzID0gdGhpcy5wbGF5ZXIuYWRkQ29tcG9uZW50KFwiSGVscGVyQ2FudmFzXCIsIG5ldyBIZWxwZXJDYW52YXModGhpcy5wbGF5ZXIpKTtcblxuICAgICAgICAgICAgY29uc3QgY29udGV4dCA9IHRoaXMuX2hlbHBlckNhbnZhcy5lbCgpO1xuICAgICAgICAgICAgdGhpcy5fdGV4dHVyZSA9IG5ldyBUSFJFRS5UZXh0dXJlKGNvbnRleHQpO1xuICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgIHRoaXMuX3RleHR1cmUgPSBuZXcgVEhSRUUuVGV4dHVyZShyZW5kZXJFbGVtZW50KTtcbiAgICAgICAgfVxuXG4gICAgICAgIHRoaXMuX3RleHR1cmUuZ2VuZXJhdGVNaXBtYXBzID0gZmFsc2U7XG4gICAgICAgIHRoaXMuX3RleHR1cmUubWluRmlsdGVyID0gVEhSRUUuTGluZWFyRmlsdGVyO1xuICAgICAgICB0aGlzLl90ZXh0dXJlLm1heEZpbHRlciA9IFRIUkVFLkxpbmVhckZpbHRlcjtcbiAgICAgICAgdGhpcy5fdGV4dHVyZS5mb3JtYXQgPSBUSFJFRS5SR0JGb3JtYXQ7XG5cbiAgICAgICAgbGV0IGVsOiBIVE1MRWxlbWVudCA9IHRoaXMuX3JlbmRlcmVyLmRvbUVsZW1lbnQ7XG4gICAgICAgIGVsLmNsYXNzTGlzdC5hZGQoJ3Zqcy1wYW5vcmFtYS1jYW52YXMnKTtcblxuICAgICAgICByZXR1cm4gZWw7XG4gICAgfVxuXG4gICAgZGlzcG9zZSgpe1xuICAgICAgICB0aGlzLmRldGFjaENvbnRyb2xFdmVudHMoKTtcbiAgICAgICAgdGhpcy5zdG9wQW5pbWF0aW9uKCk7XG4gICAgICAgIHN1cGVyLmRpc3Bvc2UoKTtcbiAgICB9XG5cbiAgICBzdGFydEFuaW1hdGlvbigpIHtcbiAgICAgICAgdGhpcy5fdGltZSA9IG5ldyBEYXRlKCkuZ2V0VGltZSgpO1xuICAgICAgICB0aGlzLmFuaW1hdGUoKTtcbiAgICB9XG5cbiAgICBzdG9wQW5pbWF0aW9uKCl7XG4gICAgICAgIGlmKHRoaXMuX3JlcXVlc3RBbmltYXRpb25JZCl7XG4gICAgICAgICAgICBjYW5jZWxBbmltYXRpb25GcmFtZSh0aGlzLl9yZXF1ZXN0QW5pbWF0aW9uSWQpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgYXR0YWNoQ29udHJvbEV2ZW50cygpOiB2b2lke1xuICAgICAgICB0aGlzLm9uKCdtb3VzZW1vdmUnLCB0aGlzLmhhbmRsZU1vdXNlTW92ZS5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vbigndG91Y2htb3ZlJywgdGhpcy5oYW5kbGVUb3VjaE1vdmUuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMub24oJ21vdXNlZG93bicsIHRoaXMuaGFuZGxlTW91c2VEb3duLmJpbmQodGhpcykpO1xuICAgICAgICB0aGlzLm9uKCd0b3VjaHN0YXJ0Jyx0aGlzLmhhbmRsZVRvdWNoU3RhcnQuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMub24oJ21vdXNldXAnLCB0aGlzLmhhbmRsZU1vdXNlVXAuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMub24oJ3RvdWNoZW5kJywgdGhpcy5oYW5kbGVUb3VjaEVuZC5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vbignbW91c2VlbnRlcicsIHRoaXMuaGFuZGxlTW91c2VFbnRlci5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vbignbW91c2VsZWF2ZScsIHRoaXMuaGFuZGxlTW91c2VMZWFzZS5iaW5kKHRoaXMpKTtcbiAgICAgICAgaWYodGhpcy5vcHRpb25zLnNjcm9sbGFibGUpe1xuICAgICAgICAgICAgdGhpcy5vbignbW91c2V3aGVlbCcsIHRoaXMuaGFuZGxlTW91c2VXaGVlbC5iaW5kKHRoaXMpKTtcbiAgICAgICAgICAgIHRoaXMub24oJ01vek1vdXNlUGl4ZWxTY3JvbGwnLCB0aGlzLmhhbmRsZU1vdXNlV2hlZWwuYmluZCh0aGlzKSk7XG4gICAgICAgIH1cbiAgICAgICAgaWYodGhpcy5vcHRpb25zLnJlc2l6YWJsZSl7XG4gICAgICAgICAgICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcihcInJlc2l6ZVwiLCB0aGlzLmhhbmRsZVJlc2l6ZS5iaW5kKHRoaXMpKTtcbiAgICAgICAgfVxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuYXV0b01vYmlsZU9yaWVudGF0aW9uKXtcbiAgICAgICAgICAgIHdpbmRvdy5hZGRFdmVudExpc3RlbmVyKCdkZXZpY2Vtb3Rpb24nLCB0aGlzLmhhbmRsZU1vYmlsZU9yaWVudGF0aW9uLmJpbmQodGhpcykpO1xuICAgICAgICB9XG4gICAgICAgIGlmKHRoaXMub3B0aW9ucy5LZXlib2FyZENvbnRyb2wpe1xuICAgICAgICAgICAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoICdrZXlkb3duJywgdGhpcy5oYW5kbGVLZXlEb3duLmJpbmQodGhpcykpO1xuICAgICAgICAgICAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoICdrZXl1cCcsIHRoaXMuaGFuZGxlS2V5VXAuYmluZCh0aGlzKSApO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgZGV0YWNoQ29udHJvbEV2ZW50cygpOiB2b2lke1xuICAgICAgICB0aGlzLm9mZignbW91c2Vtb3ZlJywgdGhpcy5oYW5kbGVNb3VzZU1vdmUuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMub2ZmKCd0b3VjaG1vdmUnLCB0aGlzLmhhbmRsZVRvdWNoTW92ZS5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vZmYoJ21vdXNlZG93bicsIHRoaXMuaGFuZGxlTW91c2VEb3duLmJpbmQodGhpcykpO1xuICAgICAgICB0aGlzLm9mZigndG91Y2hzdGFydCcsdGhpcy5oYW5kbGVUb3VjaFN0YXJ0LmJpbmQodGhpcykpO1xuICAgICAgICB0aGlzLm9mZignbW91c2V1cCcsIHRoaXMuaGFuZGxlTW91c2VVcC5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vZmYoJ3RvdWNoZW5kJywgdGhpcy5oYW5kbGVUb3VjaEVuZC5iaW5kKHRoaXMpKTtcbiAgICAgICAgdGhpcy5vZmYoJ21vdXNlZW50ZXInLCB0aGlzLmhhbmRsZU1vdXNlRW50ZXIuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMub2ZmKCdtb3VzZWxlYXZlJywgdGhpcy5oYW5kbGVNb3VzZUxlYXNlLmJpbmQodGhpcykpO1xuICAgICAgICBpZih0aGlzLm9wdGlvbnMuc2Nyb2xsYWJsZSl7XG4gICAgICAgICAgICB0aGlzLm9mZignbW91c2V3aGVlbCcsIHRoaXMuaGFuZGxlTW91c2VXaGVlbC5iaW5kKHRoaXMpKTtcbiAgICAgICAgICAgIHRoaXMub2ZmKCdNb3pNb3VzZVBpeGVsU2Nyb2xsJywgdGhpcy5oYW5kbGVNb3VzZVdoZWVsLmJpbmQodGhpcykpO1xuICAgICAgICB9XG4gICAgICAgIGlmKHRoaXMub3B0aW9ucy5yZXNpemFibGUpe1xuICAgICAgICAgICAgd2luZG93LnJlbW92ZUV2ZW50TGlzdGVuZXIoXCJyZXNpemVcIiwgdGhpcy5oYW5kbGVSZXNpemUuYmluZCh0aGlzKSk7XG4gICAgICAgIH1cbiAgICAgICAgaWYodGhpcy5vcHRpb25zLmF1dG9Nb2JpbGVPcmllbnRhdGlvbil7XG4gICAgICAgICAgICB3aW5kb3cucmVtb3ZlRXZlbnRMaXN0ZW5lcignZGV2aWNlbW90aW9uJywgdGhpcy5oYW5kbGVNb2JpbGVPcmllbnRhdGlvbi5iaW5kKHRoaXMpKTtcbiAgICAgICAgfVxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuS2V5Ym9hcmRDb250cm9sKXtcbiAgICAgICAgICAgIHdpbmRvdy5yZW1vdmVFdmVudExpc3RlbmVyKCAna2V5ZG93bicsIHRoaXMuaGFuZGxlS2V5RG93bi5iaW5kKHRoaXMpKTtcbiAgICAgICAgICAgIHdpbmRvdy5yZW1vdmVFdmVudExpc3RlbmVyKCAna2V5dXAnLCB0aGlzLmhhbmRsZUtleVVwLmJpbmQodGhpcykgKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIC8qKlxuICAgICAqIHRyaWdnZXIgd2hlbiB3aW5kb3cgcmVzaXplZFxuICAgICAqL1xuICAgIGhhbmRsZVJlc2l6ZSgpOiB2b2lke1xuICAgICAgICB0aGlzLl93aWR0aCA9IHRoaXMucGxheWVyLmVsKCkub2Zmc2V0V2lkdGgsIHRoaXMuX2hlaWdodCA9IHRoaXMucGxheWVyLmVsKCkub2Zmc2V0SGVpZ2h0O1xuICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRTaXplKCB0aGlzLl93aWR0aCwgdGhpcy5faGVpZ2h0ICk7XG4gICAgfVxuXG4gICAgaGFuZGxlTW91c2VXaGVlbChldmVudDogTW91c2VFdmVudCl7XG4gICAgICAgIGV2ZW50LnN0b3BQcm9wYWdhdGlvbigpO1xuICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgIH1cblxuICAgIGhhbmRsZU1vdXNlRW50ZXIoZXZlbnQ6IE1vdXNlRXZlbnQpIHtcbiAgICAgICAgdGhpcy5faXNVc2VySW50ZXJhY3RpbmcgPSB0cnVlO1xuICAgICAgICB0aGlzLl9hY2NlbGVjdG9yLnggPSAwO1xuICAgICAgICB0aGlzLl9hY2NlbGVjdG9yLnkgPSAwO1xuICAgIH1cblxuICAgIGhhbmRsZU1vdXNlTGVhc2UoZXZlbnQ6IE1vdXNlRXZlbnQpIHtcbiAgICAgICAgdGhpcy5faXNVc2VySW50ZXJhY3RpbmcgPSBmYWxzZTtcbiAgICAgICAgdGhpcy5fYWNjZWxlY3Rvci54ID0gMDtcbiAgICAgICAgdGhpcy5fYWNjZWxlY3Rvci55ID0gMDtcbiAgICAgICAgaWYodGhpcy5fbW91c2VEb3duKSB7XG4gICAgICAgICAgICB0aGlzLl9tb3VzZURvd24gPSBmYWxzZTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGhhbmRsZU1vdXNlRG93bihldmVudDogYW55KTogdm9pZHtcbiAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgY29uc3QgY2xpZW50WCA9IGV2ZW50LmNsaWVudFggfHwgZXZlbnQudG91Y2hlcyAmJiBldmVudC50b3VjaGVzWzBdLmNsaWVudFg7XG4gICAgICAgIGNvbnN0IGNsaWVudFkgPSBldmVudC5jbGllbnRZIHx8IGV2ZW50LnRvdWNoZXMgJiYgZXZlbnQudG91Y2hlc1swXS5jbGllbnRZO1xuICAgICAgICBpZih0eXBlb2YgY2xpZW50WCAhPT0gXCJ1bmRlZmluZWRcIiAmJiBjbGllbnRZICE9PSBcInVuZGVmaW5lZFwiKSB7XG4gICAgICAgICAgICB0aGlzLl9tb3VzZURvd24gPSB0cnVlO1xuICAgICAgICAgICAgdGhpcy5fbW91c2VEb3duUG9pbnRlci54ID0gY2xpZW50WDtcbiAgICAgICAgICAgIHRoaXMuX21vdXNlRG93blBvaW50ZXIueSA9IGNsaWVudFk7XG4gICAgICAgICAgICB0aGlzLl9tb3VzZURvd25Mb2NhdGlvbi5Mb24gPSB0aGlzLl9sb247XG4gICAgICAgICAgICB0aGlzLl9tb3VzZURvd25Mb2NhdGlvbi5MYXQgPSB0aGlzLl9sYXQ7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBoYW5kbGVNb3VzZU1vdmUoZXZlbnQ6IGFueSk6IHZvaWR7XG4gICAgICAgIGNvbnN0IGNsaWVudFggPSBldmVudC5jbGllbnRYIHx8IGV2ZW50LnRvdWNoZXMgJiYgZXZlbnQudG91Y2hlc1swXS5jbGllbnRYO1xuICAgICAgICBjb25zdCBjbGllbnRZID0gZXZlbnQuY2xpZW50WSB8fCBldmVudC50b3VjaGVzICYmIGV2ZW50LnRvdWNoZXNbMF0uY2xpZW50WTtcblxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuTW91c2VFbmFibGUgJiYgdGhpcy5jb250cm9sYWJsZSAmJiB0eXBlb2YgY2xpZW50WCAhPT0gXCJ1bmRlZmluZWRcIiAmJiB0eXBlb2YgY2xpZW50WSAhPT0gXCJ1bmRlZmluZWRcIikge1xuICAgICAgICAgICAgaWYodGhpcy5fbW91c2VEb3duKXtcbiAgICAgICAgICAgICAgICB0aGlzLl9sb24gPSAoIHRoaXMuX21vdXNlRG93blBvaW50ZXIueCAtIGNsaWVudFggKSAqIDAuMiArIHRoaXMuX21vdXNlRG93bkxvY2F0aW9uLkxvbjtcbiAgICAgICAgICAgICAgICB0aGlzLl9sYXQgPSAoIGNsaWVudFkgLSB0aGlzLl9tb3VzZURvd25Qb2ludGVyLnkgKSAqIDAuMiArIHRoaXMuX21vdXNlRG93bkxvY2F0aW9uLkxhdDtcbiAgICAgICAgICAgICAgICB0aGlzLl9hY2NlbGVjdG9yLnggPSAwO1xuICAgICAgICAgICAgICAgIHRoaXMuX2FjY2VsZWN0b3IueSA9IDA7XG4gICAgICAgICAgICB9ZWxzZSBpZighdGhpcy5vcHRpb25zLmNsaWNrQW5kRHJhZyl7XG4gICAgICAgICAgICAgICAgbGV0IHJlY3QgPSB0aGlzLmVsKCkuZ2V0Qm91bmRpbmdDbGllbnRSZWN0KCk7XG4gICAgICAgICAgICAgICAgY29uc3QgeCA9IGNsaWVudFggLSB0aGlzLl93aWR0aCAvIDIgLSByZWN0LmxlZnQ7XG4gICAgICAgICAgICAgICAgY29uc3QgeSA9IHRoaXMuX2hlaWdodCAvIDIgLSAoY2xpZW50WSAtIHJlY3QudG9wKTtcbiAgICAgICAgICAgICAgICBsZXQgYW5nbGUgPSAwO1xuICAgICAgICAgICAgICAgIGlmKHggPT09IDApe1xuICAgICAgICAgICAgICAgICAgICBhbmdsZSA9ICh5ID4gMCk/IE1hdGguUEkgLyAyIDogTWF0aC5QSSAqIDMgLyAyO1xuICAgICAgICAgICAgICAgIH1lbHNlIGlmKHggPiAwICYmIHkgPiAwKXtcbiAgICAgICAgICAgICAgICAgICAgYW5nbGUgPSBNYXRoLmF0YW4oeSAvIHgpO1xuICAgICAgICAgICAgICAgIH1lbHNlIGlmKHggPiAwICYmIHkgPCAwKXtcbiAgICAgICAgICAgICAgICAgICAgYW5nbGUgPSAyICogTWF0aC5QSSAtIE1hdGguYXRhbih5ICogLTEgLyB4KTtcbiAgICAgICAgICAgICAgICB9ZWxzZSBpZih4IDwgMCAmJiB5ID4gMCl7XG4gICAgICAgICAgICAgICAgICAgIGFuZ2xlID0gTWF0aC5QSSAtIE1hdGguYXRhbih5IC8geCAqIC0xKTtcbiAgICAgICAgICAgICAgICB9ZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIGFuZ2xlID0gTWF0aC5QSSArIE1hdGguYXRhbih5IC8geCk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIHRoaXMuX2FjY2VsZWN0b3IueCA9IE1hdGguY29zKGFuZ2xlKSAqIHRoaXMub3B0aW9ucy5tb3ZpbmdTcGVlZC54ICogTWF0aC5hYnMoeCk7XG4gICAgICAgICAgICAgICAgdGhpcy5fYWNjZWxlY3Rvci55ID0gTWF0aC5zaW4oYW5nbGUpICogdGhpcy5vcHRpb25zLm1vdmluZ1NwZWVkLnkgKiBNYXRoLmFicyh5KTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cblxuICAgIGhhbmRsZU1vdXNlVXAoZXZlbnQ6IGFueSk6IHZvaWR7XG4gICAgICAgIHRoaXMuX21vdXNlRG93biA9IGZhbHNlO1xuICAgICAgICBpZih0aGlzLm9wdGlvbnMuY2xpY2tUb1RvZ2dsZSl7XG4gICAgICAgICAgICBjb25zdCBjbGllbnRYID0gZXZlbnQuY2xpZW50WCB8fCBldmVudC5jaGFuZ2VkVG91Y2hlcyAmJiBldmVudC5jaGFuZ2VkVG91Y2hlc1swXS5jbGllbnRYO1xuICAgICAgICAgICAgY29uc3QgY2xpZW50WSA9IGV2ZW50LmNsaWVudFkgfHwgZXZlbnQuY2hhbmdlZFRvdWNoZXMgJiYgZXZlbnQuY2hhbmdlZFRvdWNoZXNbMF0uY2xpZW50WTtcbiAgICAgICAgICAgIGlmKHR5cGVvZiBjbGllbnRYICE9PSBcInVuZGVmaW5lZFwiICYmIGNsaWVudFkgIT09IFwidW5kZWZpbmVkXCIgJiYgdGhpcy5vcHRpb25zLmNsaWNrVG9Ub2dnbGUpIHtcbiAgICAgICAgICAgICAgICBjb25zdCBkaWZmWCA9IE1hdGguYWJzKGNsaWVudFggLSB0aGlzLl9tb3VzZURvd25Qb2ludGVyLngpO1xuICAgICAgICAgICAgICAgIGNvbnN0IGRpZmZZID0gTWF0aC5hYnMoY2xpZW50WSAtIHRoaXMuX21vdXNlRG93blBvaW50ZXIueSk7XG4gICAgICAgICAgICAgICAgaWYoZGlmZlggPCAwLjEgJiYgZGlmZlkgPCAwLjEpXG4gICAgICAgICAgICAgICAgICAgIHRoaXMucGxheWVyLnBhdXNlZCgpID8gdGhpcy5wbGF5ZXIucGxheSgpIDogdGhpcy5wbGF5ZXIucGF1c2UoKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cblxuICAgIGhhbmRsZVRvdWNoU3RhcnQoZXZlbnQ6IFRvdWNoRXZlbnQpIHtcbiAgICAgICAgaWYgKGV2ZW50LnRvdWNoZXMubGVuZ3RoID4gMSkge1xuICAgICAgICAgICAgdGhpcy5faXNVc2VyUGluY2ggPSB0cnVlO1xuICAgICAgICAgICAgdGhpcy5fbXVsdGlUb3VjaERpc3RhbmNlID0gZ2V0VG91Y2hlc0Rpc3RhbmNlKGV2ZW50LnRvdWNoZXMpO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuaGFuZGxlTW91c2VEb3duKGV2ZW50KTtcbiAgICB9XG5cbiAgICBoYW5kbGVUb3VjaE1vdmUoZXZlbnQ6IFRvdWNoRXZlbnQpIHtcbiAgICAgICAgdGhpcy50cmlnZ2VyKFwidG91Y2hNb3ZlXCIpO1xuICAgICAgICAvL2hhbmRsZSBzaW5nbGUgdG91Y2ggZXZlbnQsXG4gICAgICAgIGlmICghdGhpcy5faXNVc2VyUGluY2ggfHwgZXZlbnQudG91Y2hlcy5sZW5ndGggPD0gMSkge1xuICAgICAgICAgICAgdGhpcy5oYW5kbGVNb3VzZU1vdmUoZXZlbnQpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgaGFuZGxlVG91Y2hFbmQoZXZlbnQ6IFRvdWNoRXZlbnQpIHtcbiAgICAgICAgdGhpcy5faXNVc2VyUGluY2ggPSBmYWxzZTtcbiAgICAgICAgdGhpcy5oYW5kbGVNb3VzZVVwKGV2ZW50KTtcbiAgICB9XG5cbiAgICBoYW5kbGVNb2JpbGVPcmllbnRhdGlvbihldmVudDogYW55KXtcbiAgICAgICAgaWYodHlwZW9mIGV2ZW50LnJvdGF0aW9uUmF0ZSAhPT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgICAgICBjb25zdCB4ID0gZXZlbnQucm90YXRpb25SYXRlLmFscGhhO1xuICAgICAgICAgICAgY29uc3QgeSA9IGV2ZW50LnJvdGF0aW9uUmF0ZS5iZXRhO1xuICAgICAgICAgICAgY29uc3QgcG9ydHJhaXQgPSAodHlwZW9mIGV2ZW50LnBvcnRyYWl0ICE9PSBcInVuZGVmaW5lZFwiKT8gZXZlbnQucG9ydHJhaXQgOiB3aW5kb3cubWF0Y2hNZWRpYShcIihvcmllbnRhdGlvbjogcG9ydHJhaXQpXCIpLm1hdGNoZXM7XG4gICAgICAgICAgICBjb25zdCBsYW5kc2NhcGUgPSAodHlwZW9mIGV2ZW50LmxhbmRzY2FwZSAhPT0gXCJ1bmRlZmluZWRcIik/IGV2ZW50LmxhbmRzY2FwZSA6IHdpbmRvdy5tYXRjaE1lZGlhKFwiKG9yaWVudGF0aW9uOiBsYW5kc2NhcGUpXCIpLm1hdGNoZXM7XG4gICAgICAgICAgICBjb25zdCBvcmllbnRhdGlvbiA9IGV2ZW50Lm9yaWVudGF0aW9uIHx8IHdpbmRvdy5vcmllbnRhdGlvbjtcblxuICAgICAgICAgICAgaWYgKHBvcnRyYWl0KSB7XG4gICAgICAgICAgICAgICAgdGhpcy5fbG9uID0gdGhpcy5fbG9uIC0geSAqIHRoaXMub3B0aW9ucy5tb2JpbGVWaWJyYXRpb25WYWx1ZTtcbiAgICAgICAgICAgICAgICB0aGlzLl9sYXQgPSB0aGlzLl9sYXQgKyB4ICogdGhpcy5vcHRpb25zLm1vYmlsZVZpYnJhdGlvblZhbHVlO1xuICAgICAgICAgICAgfWVsc2UgaWYobGFuZHNjYXBlKXtcbiAgICAgICAgICAgICAgICBsZXQgb3JpZW50YXRpb25EZWdyZWUgPSAtOTA7XG4gICAgICAgICAgICAgICAgaWYodHlwZW9mIG9yaWVudGF0aW9uICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgICAgICAgICAgb3JpZW50YXRpb25EZWdyZWUgPSBvcmllbnRhdGlvbjtcbiAgICAgICAgICAgICAgICB9XG5cbiAgICAgICAgICAgICAgICB0aGlzLl9sb24gPSAob3JpZW50YXRpb25EZWdyZWUgPT09IC05MCk/IHRoaXMuX2xvbiArIHggKiB0aGlzLm9wdGlvbnMubW9iaWxlVmlicmF0aW9uVmFsdWUgOiB0aGlzLl9sb24gLSB4ICogdGhpcy5vcHRpb25zLm1vYmlsZVZpYnJhdGlvblZhbHVlO1xuICAgICAgICAgICAgICAgIHRoaXMuX2xhdCA9IChvcmllbnRhdGlvbkRlZ3JlZSA9PT0gLTkwKT8gdGhpcy5fbGF0ICsgeSAqIHRoaXMub3B0aW9ucy5tb2JpbGVWaWJyYXRpb25WYWx1ZSA6IHRoaXMuX2xhdCAtIHkgKiB0aGlzLm9wdGlvbnMubW9iaWxlVmlicmF0aW9uVmFsdWU7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBoYW5kbGVLZXlEb3duKGV2ZW50OiBhbnkpe1xuICAgICAgICB0aGlzLl9pc1VzZXJJbnRlcmFjdGluZyA9IHRydWU7XG4gICAgICAgIHN3aXRjaChldmVudC5rZXlDb2RlKXtcbiAgICAgICAgICAgIGNhc2UgMzg6IC8qdXAqL1xuICAgICAgICAgICAgY2FzZSA4NzogLypXKi9cbiAgICAgICAgICAgICAgICB0aGlzLl9sYXQgKz0gdGhpcy5vcHRpb25zLktleWJvYXJkTW92aW5nU3BlZWQueTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIGNhc2UgMzc6IC8qbGVmdCovXG4gICAgICAgICAgICBjYXNlIDY1OiAvKkEqL1xuICAgICAgICAgICAgICAgIHRoaXMuX2xvbiAtPSB0aGlzLm9wdGlvbnMuS2V5Ym9hcmRNb3ZpbmdTcGVlZC54O1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgY2FzZSAzOTogLypyaWdodCovXG4gICAgICAgICAgICBjYXNlIDY4OiAvKkQqL1xuICAgICAgICAgICAgICAgIHRoaXMuX2xvbiArPSB0aGlzLm9wdGlvbnMuS2V5Ym9hcmRNb3ZpbmdTcGVlZC54O1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgY2FzZSA0MDogLypkb3duKi9cbiAgICAgICAgICAgIGNhc2UgODM6IC8qUyovXG4gICAgICAgICAgICAgICAgdGhpcy5fbGF0IC09IHRoaXMub3B0aW9ucy5LZXlib2FyZE1vdmluZ1NwZWVkLnk7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBoYW5kbGVLZXlVcChldmVudDogYW55KXtcbiAgICAgICAgdGhpcy5faXNVc2VySW50ZXJhY3RpbmcgPSBmYWxzZTtcbiAgICB9XG5cbiAgICBlbmFibGVWUigpIHtcbiAgICAgICAgdGhpcy5fVlJNb2RlID0gdHJ1ZTtcbiAgICB9XG5cbiAgICBkaXNhYmxlVlIoKSB7XG4gICAgICAgIHRoaXMuX1ZSTW9kZSA9IGZhbHNlO1xuICAgIH1cblxuXG4gICAgYW5pbWF0ZSgpe1xuICAgICAgICB0aGlzLl9yZXF1ZXN0QW5pbWF0aW9uSWQgPSByZXF1ZXN0QW5pbWF0aW9uRnJhbWUoIHRoaXMuYW5pbWF0ZS5iaW5kKHRoaXMpICk7XG4gICAgICAgIGxldCBjdCA9IG5ldyBEYXRlKCkuZ2V0VGltZSgpO1xuICAgICAgICBpZiAoY3QgLSB0aGlzLl90aW1lID49IDMwKSB7XG4gICAgICAgICAgICB0aGlzLl90ZXh0dXJlLm5lZWRzVXBkYXRlID0gdHJ1ZTtcbiAgICAgICAgICAgIHRoaXMuX3RpbWUgPSBjdDtcbiAgICAgICAgICAgIHRoaXMudHJpZ2dlcihcInRleHR1cmVSZW5kZXJcIik7XG4gICAgICAgIH1cblxuICAgICAgICAvL2NhbnZhcyBzaG91bGQgb25seSBiZSByZW5kZXJlZCB3aGVuIHZpZGVvIGlzIHJlYWR5IG9yIHdpbGwgcmVwb3J0IGBubyB2aWRlb2Agd2FybmluZyBtZXNzYWdlLlxuICAgICAgICBpZih0aGlzLl9yZW5kZXJFbGVtZW50LnRhZ05hbWUudG9Mb3dlckNhc2UoKSAhPT0gXCJ2aWRlb1wiIHx8IHRoaXMucGxheWVyLnJlYWR5U3RhdGUoKSA+PSBIQVZFX0NVUlJFTlRfREFUQSl7XG4gICAgICAgICAgICB0aGlzLnJlbmRlcigpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgcmVuZGVyKCl7XG4gICAgICAgIHRoaXMudHJpZ2dlcihcImJlZm9yZVJlbmRlclwiKTtcbiAgICAgICAgaWYodGhpcy5fY29udHJvbGFibGUpe1xuICAgICAgICAgICAgaWYoIXRoaXMuX2lzVXNlckludGVyYWN0aW5nKXtcbiAgICAgICAgICAgICAgICBsZXQgc3ltYm9sTGF0ID0gKHRoaXMuX2xhdCA+IHRoaXMub3B0aW9ucy5pbml0TGF0KT8gIC0xIDogMTtcbiAgICAgICAgICAgICAgICBsZXQgc3ltYm9sTG9uID0gKHRoaXMuX2xvbiA+IHRoaXMub3B0aW9ucy5pbml0TG9uKT8gIC0xIDogMTtcbiAgICAgICAgICAgICAgICBpZih0aGlzLm9wdGlvbnMuYmFja1RvSW5pdExhdCl7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuX2xhdCA9IChcbiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXMuX2xhdCA+ICh0aGlzLm9wdGlvbnMuaW5pdExhdCAtIE1hdGguYWJzKHRoaXMub3B0aW9ucy5yZXR1cm5MYXRTcGVlZCkpICYmXG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLl9sYXQgPCAodGhpcy5vcHRpb25zLmluaXRMYXQgKyBNYXRoLmFicyh0aGlzLm9wdGlvbnMucmV0dXJuTGF0U3BlZWQpKVxuICAgICAgICAgICAgICAgICAgICApPyB0aGlzLm9wdGlvbnMuaW5pdExhdCA6IHRoaXMuX2xhdCArIHRoaXMub3B0aW9ucy5yZXR1cm5MYXRTcGVlZCAqIHN5bWJvbExhdDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgaWYodGhpcy5vcHRpb25zLmJhY2tUb0luaXRMb24pe1xuICAgICAgICAgICAgICAgICAgICB0aGlzLl9sb24gPSAoXG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLl9sb24gPiAodGhpcy5vcHRpb25zLmluaXRMb24gLSBNYXRoLmFicyh0aGlzLm9wdGlvbnMucmV0dXJuTG9uU3BlZWQpKSAmJlxuICAgICAgICAgICAgICAgICAgICAgICAgdGhpcy5fbG9uIDwgKHRoaXMub3B0aW9ucy5pbml0TG9uICsgTWF0aC5hYnModGhpcy5vcHRpb25zLnJldHVybkxvblNwZWVkKSlcbiAgICAgICAgICAgICAgICAgICAgKT8gdGhpcy5vcHRpb25zLmluaXRMb24gOiB0aGlzLl9sb24gKyB0aGlzLm9wdGlvbnMucmV0dXJuTG9uU3BlZWQgKiBzeW1ib2xMb247XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfWVsc2UgaWYodGhpcy5fYWNjZWxlY3Rvci54ICE9PSAwICYmIHRoaXMuX2FjY2VsZWN0b3IueSAhPT0gMCl7XG4gICAgICAgICAgICAgICAgdGhpcy5fbGF0ICs9IHRoaXMuX2FjY2VsZWN0b3IueTtcbiAgICAgICAgICAgICAgICB0aGlzLl9sb24gKz0gdGhpcy5fYWNjZWxlY3Rvci54O1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG5cbiAgICAgICAgaWYodGhpcy5fb3B0aW9ucy5taW5Mb24gPT09IDAgJiYgdGhpcy5fb3B0aW9ucy5tYXhMb24gPT09IDM2MCl7XG4gICAgICAgICAgICBpZih0aGlzLl9sb24gPiAzNjApe1xuICAgICAgICAgICAgICAgIHRoaXMuX2xvbiAtPSAzNjA7XG4gICAgICAgICAgICB9ZWxzZSBpZih0aGlzLl9sb24gPCAwKXtcbiAgICAgICAgICAgICAgICB0aGlzLl9sb24gKz0gMzYwO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG5cbiAgICAgICAgdGhpcy5fbGF0ID0gTWF0aC5tYXgoIHRoaXMub3B0aW9ucy5taW5MYXQsIE1hdGgubWluKCB0aGlzLm9wdGlvbnMubWF4TGF0LCB0aGlzLl9sYXQgKSApO1xuICAgICAgICB0aGlzLl9sb24gPSBNYXRoLm1heCggdGhpcy5vcHRpb25zLm1pbkxvbiwgTWF0aC5taW4oIHRoaXMub3B0aW9ucy5tYXhMb24sIHRoaXMuX2xvbiApICk7XG4gICAgICAgIHRoaXMuX3BoaSA9IFRIUkVFLk1hdGguZGVnVG9SYWQoIDkwIC0gdGhpcy5fbGF0ICk7XG4gICAgICAgIHRoaXMuX3RoZXRhID0gVEhSRUUuTWF0aC5kZWdUb1JhZCggdGhpcy5fbG9uICk7XG5cbiAgICAgICAgaWYodGhpcy5faGVscGVyQ2FudmFzKXtcbiAgICAgICAgICAgIHRoaXMuX2hlbHBlckNhbnZhcy5yZW5kZXIoKTtcbiAgICAgICAgfVxuICAgICAgICB0aGlzLl9yZW5kZXJlci5jbGVhcigpO1xuICAgICAgICB0aGlzLnRyaWdnZXIoXCJyZW5kZXJcIik7XG4gICAgfVxuXG4gICAgZ2V0IFZSTW9kZSgpOiBib29sZWFue1xuICAgICAgICByZXR1cm4gdGhpcy5fVlJNb2RlO1xuICAgIH1cblxuICAgIGdldCBjb250cm9sYWJsZSgpOiBib29sZWFue1xuICAgICAgICByZXR1cm4gdGhpcy5fY29udHJvbGFibGU7XG4gICAgfVxuXG4gICAgc2V0IGNvbnRyb2xhYmxlKHZhbDogYm9vbGVhbik6IHZvaWR7XG4gICAgICAgIHRoaXMuX2NvbnRyb2xhYmxlID0gdmFsO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgQmFzZUNhbnZhczsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdHlwZSB7IFBsYXllcn0gZnJvbSAnLi4vdHlwZXMvaW5kZXgnO1xuaW1wb3J0IENsaWNrYWJsZUNvbXBvbmVudCBmcm9tICcuL0NsaWNrYWJsZUNvbXBvbmVudCc7XG5cbmNsYXNzIEJ1dHRvbiBleHRlbmRzIENsaWNrYWJsZUNvbXBvbmVudHtcbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczogYW55ID0ge30pe1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMpO1xuICAgICAgICB0aGlzLm9uKFwia2V5ZG93blwiLCB0aGlzLmhhbmRsZUtleVByZXNzLmJpbmQodGhpcykpO1xuICAgIH1cblxuICAgIGNyZWF0ZUVsKHRhZ05hbWU6IHN0cmluZywgcHJvcGVydGllcz86IGFueSwgYXR0cmlidXRlcz86IGFueSl7XG4gICAgICAgIHJldHVybiBzdXBlci5jcmVhdGVFbChcImJ1dHRvblwiLCBudWxsLCB7XG4gICAgICAgICAgICB0eXBlOiBcImJ1dHRvblwiLFxuICAgICAgICAgICAgLy8gbGV0IHRoZSBzY3JlZW4gcmVhZGVyIHVzZXIga25vdyB0aGF0IHRoZSB0ZXh0IG9mIHRoZSBidXR0b24gbWF5IGNoYW5nZVxuICAgICAgICAgICAgJ2FyaWEtbGl2ZSc6ICdwb2xpdGUnXG4gICAgICAgIH0pXG4gICAgfVxuXG4gICAgLyoqXG4gICAgICogRW5hYmxlIHRoZSBgQnV0dG9uYCBlbGVtZW50IHNvIHRoYXQgaXQgY2FuIGJlIGFjdGl2YXRlZCBvciBjbGlja2VkLiBVc2UgdGhpcyB3aXRoXG4gICAgICoge0BsaW5rIEJ1dHRvbiNkaXNhYmxlfS5cbiAgICAgKi9cbiAgICBlbmFibGUoKSB7XG4gICAgICAgIHRoaXMuZWwoKS5yZW1vdmVBdHRyaWJ1dGUoJ2Rpc2FibGVkJyk7XG4gICAgfVxuXG4gICAgLyoqXG4gICAgICogRW5hYmxlIHRoZSBgQnV0dG9uYCBlbGVtZW50IHNvIHRoYXQgaXQgY2Fubm90IGJlIGFjdGl2YXRlZCBvciBjbGlja2VkLiBVc2UgdGhpcyB3aXRoXG4gICAgICoge0BsaW5rIEJ1dHRvbiNlbmFibGV9LlxuICAgICAqL1xuICAgIGRpc2FibGUoKSB7XG4gICAgICAgIHRoaXMuZWwoKS5zZXRBdHRyaWJ1dGUoJ2Rpc2FibGVkJywgJ2Rpc2FibGVkJyk7XG4gICAgfVxuXG4gICAgaGFuZGxlS2V5UHJlc3MoZXZlbnQ6IEV2ZW50KXtcbiAgICAgICAgLy8gSWdub3JlIFNwYWNlICgzMikgb3IgRW50ZXIgKDEzKSBrZXkgb3BlcmF0aW9uLCB3aGljaCBpcyBoYW5kbGVkIGJ5IHRoZSBicm93c2VyIGZvciBhIGJ1dHRvbi5cbiAgICAgICAgaWYgKGV2ZW50LndoaWNoID09PSAzMiB8fCBldmVudC53aGljaCA9PT0gMTMpIHtcbiAgICAgICAgICAgIHJldHVybjtcbiAgICAgICAgfVxuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgQnV0dG9uOyIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyIH0gZnJvbSAnLi4vdHlwZXMnO1xuaW1wb3J0IENvbXBvbmVudCBmcm9tICcuL0NvbXBvbmVudCc7XG5cbmNsYXNzIENsaWNrYWJsZUNvbXBvbmVudCBleHRlbmRzIENvbXBvbmVudHtcblxuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBhbnkgPSB7fSl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucyk7XG4gICAgICAgIHRoaXMub24oXCJjbGlja1wiLCB0aGlzLmhhbmRsZUNsaWNrLmJpbmQodGhpcykpO1xuICAgICAgICB0aGlzLmFkZExpc3RlbmVyKFwidGFwXCIsIHRoaXMuaGFuZGxlQ2xpY2suYmluZCh0aGlzKSk7XG4gICAgfVxuXG4gICAgLyoqXG4gICAgICogQnVpbGRzIHRoZSBkZWZhdWx0IERPTSBgY2xhc3NOYW1lYC5cbiAgICAgKlxuICAgICAqIEByZXR1cm4ge3N0cmluZ31cbiAgICAgKiAgICAgICAgIFRoZSBET00gYGNsYXNzTmFtZWAgZm9yIHRoaXMgb2JqZWN0LlxuICAgICAqL1xuICAgIGJ1aWxkQ1NTQ2xhc3MoKSB7XG4gICAgICAgIHJldHVybiBgdmpzLWNvbnRyb2wgdmpzLWJ1dHRvbiAke3N1cGVyLmJ1aWxkQ1NTQ2xhc3MoKX1gO1xuICAgIH1cblxuICAgIGhhbmRsZUNsaWNrKGV2ZW50OiBFdmVudCkge1xuICAgICAgICB0aGlzLnRyaWdnZXIoXCJjbGlja1wiKTtcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IENsaWNrYWJsZUNvbXBvbmVudDsiLCIvLyBAIGZsb3dcblxuaW1wb3J0IEV2ZW50RW1pdHRlciBmcm9tICd3b2xmeTg3LWV2ZW50ZW1pdHRlcic7XG5pbXBvcnQgdHlwZSB7IFBsYXllciB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCB7IG1lcmdlT3B0aW9ucywgQ29tcG9uZW50RGF0YSB9IGZyb20gJy4uL3V0aWxzJztcblxuLyoqXG4gKiBiYXNlIENvbXBvbmVudCBsYXllciwgd2hpY2ggd2lsbCBiZSB1c2Ugd2hlbiB2aWRlb2pzIGlzIG5vdCBzdXBwb3J0ZWQgZW52aXJvbm1lbnQuXG4gKi9cbmNsYXNzIENvbXBvbmVudCBleHRlbmRzIEV2ZW50RW1pdHRlcntcbiAgICBfb3B0aW9uczogYW55O1xuICAgIF9pZDogc3RyaW5nO1xuICAgIF9lbDogSFRNTEVsZW1lbnQgfCBudWxsO1xuICAgIF9wbGF5ZXI6IFBsYXllcjtcbiAgICBfcmVuZGVyRWxlbWVudDogSFRNTEVsZW1lbnQ7XG4gICAgX2NoaWxkcmVuOiBDb21wb25lbnREYXRhW107XG5cbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczogYW55ID0ge30sIHJlbmRlckVsZW1lbnQ/OiBIVE1MRWxlbWVudCwgcmVhZHk/OiAoKSA9PiB2b2lkKXtcbiAgICAgICAgc3VwZXIoKTtcblxuICAgICAgICB0aGlzLl9wbGF5ZXIgPSBwbGF5ZXI7XG4gICAgICAgIC8vIE1ha2UgYSBjb3B5IG9mIHByb3RvdHlwZS5vcHRpb25zXyB0byBwcm90ZWN0IGFnYWluc3Qgb3ZlcnJpZGluZyBkZWZhdWx0c1xuICAgICAgICB0aGlzLl9vcHRpb25zID0gbWVyZ2VPcHRpb25zKHt9LCB0aGlzLl9vcHRpb25zKTtcbiAgICAgICAgLy8gVXBkYXRlZCBvcHRpb25zIHdpdGggc3VwcGxpZWQgb3B0aW9uc1xuICAgICAgICB0aGlzLl9vcHRpb25zID0gbWVyZ2VPcHRpb25zKHRoaXMuX29wdGlvbnMsIG9wdGlvbnMpO1xuXG4gICAgICAgIHRoaXMuX3JlbmRlckVsZW1lbnQgPSByZW5kZXJFbGVtZW50O1xuXG4gICAgICAgIC8vIEdldCBJRCBmcm9tIG9wdGlvbnMgb3Igb3B0aW9ucyBlbGVtZW50IGlmIG9uZSBpcyBzdXBwbGllZFxuICAgICAgICB0aGlzLl9pZCA9IG9wdGlvbnMuaWQgfHwgKG9wdGlvbnMuZWwgJiYgb3B0aW9ucy5lbC5pZCk7XG5cbiAgICAgICAgdGhpcy5fZWwgPSAob3B0aW9ucy5lbCk/IG9wdGlvbnMuZWwgOiB0aGlzLmNyZWF0ZUVsKCk7XG5cbiAgICAgICAgdGhpcy5lbWl0VGFwRXZlbnRzKCk7XG5cbiAgICAgICAgdGhpcy5fY2hpbGRyZW4gPSBbXTtcblxuICAgICAgICBpZihyZWFkeSl7XG4gICAgICAgICAgICByZWFkeS5jYWxsKHRoaXMpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgZGlzcG9zZSgpe1xuICAgICAgICBmb3IobGV0IGkgPSAwOyBpIDwgdGhpcy5fY2hpbGRyZW4ubGVuZ3RoOyBpKyspe1xuICAgICAgICAgICAgdGhpcy5fY2hpbGRyZW5baV0uY29tcG9uZW50LmRpc3Bvc2UoKTtcbiAgICAgICAgfVxuXG4gICAgICAgIGlmKHRoaXMuX2VsKXtcbiAgICAgICAgICAgIGlmKHRoaXMuX2VsLnBhcmVudE5vZGUpe1xuICAgICAgICAgICAgICAgIHRoaXMuX2VsLnBhcmVudE5vZGUucmVtb3ZlQ2hpbGQodGhpcy5fZWwpO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICB0aGlzLl9lbCA9IG51bGw7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICAvKipcbiAgICAgKiBFbWl0IGEgJ3RhcCcgZXZlbnRzIHdoZW4gdG91Y2ggZXZlbnQgc3VwcG9ydCBnZXRzIGRldGVjdGVkLiBUaGlzIGdldHMgdXNlZCB0b1xuICAgICAqIHN1cHBvcnQgdG9nZ2xpbmcgdGhlIGNvbnRyb2xzIHRocm91Z2ggYSB0YXAgb24gdGhlIHZpZGVvLiBUaGV5IGdldCBlbmFibGVkXG4gICAgICogYmVjYXVzZSBldmVyeSBzdWItY29tcG9uZW50IHdvdWxkIGhhdmUgZXh0cmEgb3ZlcmhlYWQgb3RoZXJ3aXNlLlxuICAgICAqICovXG4gICAgZW1pdFRhcEV2ZW50cygpIHtcbiAgICAgICAgLy8gVHJhY2sgdGhlIHN0YXJ0IHRpbWUgc28gd2UgY2FuIGRldGVybWluZSBob3cgbG9uZyB0aGUgdG91Y2ggbGFzdGVkXG4gICAgICAgIGxldCB0b3VjaFN0YXJ0ID0gMDtcbiAgICAgICAgbGV0IGZpcnN0VG91Y2ggPSBudWxsO1xuXG4gICAgICAgIC8vIE1heGltdW0gbW92ZW1lbnQgYWxsb3dlZCBkdXJpbmcgYSB0b3VjaCBldmVudCB0byBzdGlsbCBiZSBjb25zaWRlcmVkIGEgdGFwXG4gICAgICAgIC8vIE90aGVyIHBvcHVsYXIgbGlicyB1c2UgYW55d2hlcmUgZnJvbSAyIChoYW1tZXIuanMpIHRvIDE1LFxuICAgICAgICAvLyBzbyAxMCBzZWVtcyBsaWtlIGEgbmljZSwgcm91bmQgbnVtYmVyLlxuICAgICAgICBjb25zdCB0YXBNb3ZlbWVudFRocmVzaG9sZCA9IDEwO1xuXG4gICAgICAgIC8vIFRoZSBtYXhpbXVtIGxlbmd0aCBhIHRvdWNoIGNhbiBiZSB3aGlsZSBzdGlsbCBiZWluZyBjb25zaWRlcmVkIGEgdGFwXG4gICAgICAgIGNvbnN0IHRvdWNoVGltZVRocmVzaG9sZCA9IDIwMDtcblxuICAgICAgICBsZXQgY291bGRCZVRhcDtcblxuICAgICAgICB0aGlzLm9uKCd0b3VjaHN0YXJ0JywgZnVuY3Rpb24oZXZlbnQpIHtcbiAgICAgICAgICAgIC8vIElmIG1vcmUgdGhhbiBvbmUgZmluZ2VyLCBkb24ndCBjb25zaWRlciB0cmVhdGluZyB0aGlzIGFzIGEgY2xpY2tcbiAgICAgICAgICAgIGlmIChldmVudC50b3VjaGVzLmxlbmd0aCA9PT0gMSkge1xuICAgICAgICAgICAgICAgIC8vIENvcHkgcGFnZVgvcGFnZVkgZnJvbSB0aGUgb2JqZWN0XG4gICAgICAgICAgICAgICAgZmlyc3RUb3VjaCA9IHtcbiAgICAgICAgICAgICAgICAgICAgcGFnZVg6IGV2ZW50LnRvdWNoZXNbMF0ucGFnZVgsXG4gICAgICAgICAgICAgICAgICAgIHBhZ2VZOiBldmVudC50b3VjaGVzWzBdLnBhZ2VZXG4gICAgICAgICAgICAgICAgfTtcbiAgICAgICAgICAgICAgICAvLyBSZWNvcmQgc3RhcnQgdGltZSBzbyB3ZSBjYW4gZGV0ZWN0IGEgdGFwIHZzLiBcInRvdWNoIGFuZCBob2xkXCJcbiAgICAgICAgICAgICAgICB0b3VjaFN0YXJ0ID0gbmV3IERhdGUoKS5nZXRUaW1lKCk7XG4gICAgICAgICAgICAgICAgLy8gUmVzZXQgY291bGRCZVRhcCB0cmFja2luZ1xuICAgICAgICAgICAgICAgIGNvdWxkQmVUYXAgPSB0cnVlO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICB0aGlzLm9uKCd0b3VjaG1vdmUnLCBmdW5jdGlvbihldmVudCkge1xuICAgICAgICAgICAgLy8gSWYgbW9yZSB0aGFuIG9uZSBmaW5nZXIsIGRvbid0IGNvbnNpZGVyIHRyZWF0aW5nIHRoaXMgYXMgYSBjbGlja1xuICAgICAgICAgICAgaWYgKGV2ZW50LnRvdWNoZXMubGVuZ3RoID4gMSkge1xuICAgICAgICAgICAgICAgIGNvdWxkQmVUYXAgPSBmYWxzZTtcbiAgICAgICAgICAgIH0gZWxzZSBpZiAoZmlyc3RUb3VjaCkge1xuICAgICAgICAgICAgICAgIC8vIFNvbWUgZGV2aWNlcyB3aWxsIHRocm93IHRvdWNobW92ZXMgZm9yIGFsbCBidXQgdGhlIHNsaWdodGVzdCBvZiB0YXBzLlxuICAgICAgICAgICAgICAgIC8vIFNvLCBpZiB3ZSBtb3ZlZCBvbmx5IGEgc21hbGwgZGlzdGFuY2UsIHRoaXMgY291bGQgc3RpbGwgYmUgYSB0YXBcbiAgICAgICAgICAgICAgICBjb25zdCB4ZGlmZiA9IGV2ZW50LnRvdWNoZXNbMF0ucGFnZVggLSBmaXJzdFRvdWNoLnBhZ2VYO1xuICAgICAgICAgICAgICAgIGNvbnN0IHlkaWZmID0gZXZlbnQudG91Y2hlc1swXS5wYWdlWSAtIGZpcnN0VG91Y2gucGFnZVk7XG4gICAgICAgICAgICAgICAgY29uc3QgdG91Y2hEaXN0YW5jZSA9IE1hdGguc3FydCh4ZGlmZiAqIHhkaWZmICsgeWRpZmYgKiB5ZGlmZik7XG5cbiAgICAgICAgICAgICAgICBpZiAodG91Y2hEaXN0YW5jZSA+IHRhcE1vdmVtZW50VGhyZXNob2xkKSB7XG4gICAgICAgICAgICAgICAgICAgIGNvdWxkQmVUYXAgPSBmYWxzZTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuXG4gICAgICAgIGNvbnN0IG5vVGFwID0gZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICBjb3VsZEJlVGFwID0gZmFsc2U7XG4gICAgICAgIH07XG5cbiAgICAgICAgLy8gVE9ETzogTGlzdGVuIHRvIHRoZSBvcmlnaW5hbCB0YXJnZXQuIGh0dHA6Ly95b3V0dS5iZS9EdWpmcFhPS1VwOD90PTEzbThzXG4gICAgICAgIHRoaXMub24oJ3RvdWNobGVhdmUnLCBub1RhcCk7XG4gICAgICAgIHRoaXMub24oJ3RvdWNoY2FuY2VsJywgbm9UYXApO1xuXG4gICAgICAgIC8vIFdoZW4gdGhlIHRvdWNoIGVuZHMsIG1lYXN1cmUgaG93IGxvbmcgaXQgdG9vayBhbmQgdHJpZ2dlciB0aGUgYXBwcm9wcmlhdGVcbiAgICAgICAgLy8gZXZlbnRcbiAgICAgICAgdGhpcy5vbigndG91Y2hlbmQnLCAoZXZlbnQpID0+IHtcbiAgICAgICAgICAgIGZpcnN0VG91Y2ggPSBudWxsO1xuICAgICAgICAgICAgLy8gUHJvY2VlZCBvbmx5IGlmIHRoZSB0b3VjaG1vdmUvbGVhdmUvY2FuY2VsIGV2ZW50IGRpZG4ndCBoYXBwZW5cbiAgICAgICAgICAgIGlmIChjb3VsZEJlVGFwID09PSB0cnVlKSB7XG4gICAgICAgICAgICAgICAgLy8gTWVhc3VyZSBob3cgbG9uZyB0aGUgdG91Y2ggbGFzdGVkXG4gICAgICAgICAgICAgICAgY29uc3QgdG91Y2hUaW1lID0gbmV3IERhdGUoKS5nZXRUaW1lKCkgLSB0b3VjaFN0YXJ0O1xuXG4gICAgICAgICAgICAgICAgLy8gTWFrZSBzdXJlIHRoZSB0b3VjaCB3YXMgbGVzcyB0aGFuIHRoZSB0aHJlc2hvbGQgdG8gYmUgY29uc2lkZXJlZCBhIHRhcFxuICAgICAgICAgICAgICAgIGlmICh0b3VjaFRpbWUgPCB0b3VjaFRpbWVUaHJlc2hvbGQpIHtcbiAgICAgICAgICAgICAgICAgICAgLy8gRG9uJ3QgbGV0IGJyb3dzZXIgdHVybiB0aGlzIGludG8gYSBjbGlja1xuICAgICAgICAgICAgICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgICAgICAgICAvKipcbiAgICAgICAgICAgICAgICAgICAgICogVHJpZ2dlcmVkIHdoZW4gYSBgQ29tcG9uZW50YCBpcyB0YXBwZWQuXG4gICAgICAgICAgICAgICAgICAgICAqXG4gICAgICAgICAgICAgICAgICAgICAqIEBldmVudCBDb21wb25lbnQjdGFwXG4gICAgICAgICAgICAgICAgICAgICAqIEB0eXBlIHtFdmVudFRhcmdldH5FdmVudH1cbiAgICAgICAgICAgICAgICAgICAgICovXG4gICAgICAgICAgICAgICAgICAgIHRoaXMudHJpZ2dlcigndGFwJyk7XG4gICAgICAgICAgICAgICAgICAgIC8vIEl0IG1heSBiZSBnb29kIHRvIGNvcHkgdGhlIHRvdWNoZW5kIGV2ZW50IG9iamVjdCBhbmQgY2hhbmdlIHRoZVxuICAgICAgICAgICAgICAgICAgICAvLyB0eXBlIHRvIHRhcCwgaWYgdGhlIG90aGVyIGV2ZW50IHByb3BlcnRpZXMgYXJlbid0IGV4YWN0IGFmdGVyXG4gICAgICAgICAgICAgICAgICAgIC8vIEV2ZW50cy5maXhFdmVudCBydW5zIChlLmcuIGV2ZW50LnRhcmdldClcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIGNyZWF0ZUVsKHRhZ05hbWU/OiBzdHJpbmcgPSBcImRpdlwiLCBwcm9wZXJ0aWVzPzogYW55LCBhdHRyaWJ1dGVzPzogYW55KTogSFRNTEVsZW1lbnR7XG4gICAgICAgIGxldCBlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQodGFnTmFtZSk7XG4gICAgICAgIGVsLmNsYXNzTmFtZSA9IHRoaXMuYnVpbGRDU1NDbGFzcygpO1xuXG4gICAgICAgIGZvcihsZXQgYXR0cmlidXRlIGluIGF0dHJpYnV0ZXMpe1xuICAgICAgICAgICAgaWYoYXR0cmlidXRlcy5oYXNPd25Qcm9wZXJ0eShhdHRyaWJ1dGUpKXtcbiAgICAgICAgICAgICAgICBsZXQgdmFsdWUgPSBhdHRyaWJ1dGVzW2F0dHJpYnV0ZV07XG4gICAgICAgICAgICAgICAgZWwuc2V0QXR0cmlidXRlKGF0dHJpYnV0ZSwgdmFsdWUpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBlbDtcbiAgICB9XG5cbiAgICBlbCgpOiBIVE1MRWxlbWVudHtcbiAgICAgICAgcmV0dXJuIHRoaXMuX2VsO1xuICAgIH1cblxuICAgIC8qKlxuICAgICAqIEJ1aWxkcyB0aGUgZGVmYXVsdCBET00gY2xhc3MgbmFtZS4gU2hvdWxkIGJlIG92ZXJyaWRlbiBieSBzdWItY29tcG9uZW50cy5cbiAgICAgKlxuICAgICAqIEByZXR1cm4ge3N0cmluZ31cbiAgICAgKiAgICAgICAgIFRoZSBET00gY2xhc3MgbmFtZSBmb3IgdGhpcyBvYmplY3QuXG4gICAgICpcbiAgICAgKiBAYWJzdHJhY3RcbiAgICAgKi9cbiAgICBidWlsZENTU0NsYXNzKCkge1xuICAgICAgICAvLyBDaGlsZCBjbGFzc2VzIGNhbiBpbmNsdWRlIGEgZnVuY3Rpb24gdGhhdCBkb2VzOlxuICAgICAgICAvLyByZXR1cm4gJ0NMQVNTIE5BTUUnICsgdGhpcy5fc3VwZXIoKTtcbiAgICAgICAgcmV0dXJuICcnO1xuICAgIH1cblxuICAgIG9uKG5hbWU6IHN0cmluZywgYWN0aW9uOiBGdW5jdGlvbik6IHZvaWR7XG4gICAgICAgIHRoaXMuZWwoKS5hZGRFdmVudExpc3RlbmVyKG5hbWUsIGFjdGlvbik7XG4gICAgfVxuXG4gICAgb2ZmKG5hbWU6IHN0cmluZywgYWN0aW9uOiBGdW5jdGlvbik6IHZvaWR7XG4gICAgICAgIHRoaXMuZWwoKS5yZW1vdmVFdmVudExpc3RlbmVyKG5hbWUsIGFjdGlvbik7XG4gICAgfVxuXG4gICAgb25lKG5hbWU6IHN0cmluZywgYWN0aW9uOiBGdW5jdGlvbik6IHZvaWR7XG4gICAgICAgIGxldCBvbmVUaW1lRnVuY3Rpb247XG4gICAgICAgIHRoaXMub24obmFtZSwgb25lVGltZUZ1bmN0aW9uID0gKCk9PntcbiAgICAgICAgICAgYWN0aW9uKCk7XG4gICAgICAgICAgIHRoaXMub2ZmKG5hbWUsIG9uZVRpbWVGdW5jdGlvbik7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIC8vRG8gbm90aGluZyBieSBkZWZhdWx0XG4gICAgaGFuZGxlUmVzaXplKCk6IHZvaWR7XG4gICAgfVxuXG4gICAgYWRkQ2xhc3MobmFtZTogc3RyaW5nKXtcbiAgICAgICAgdGhpcy5lbCgpLmNsYXNzTGlzdC5hZGQobmFtZSk7XG4gICAgfVxuXG4gICAgcmVtb3ZlQ2xhc3MobmFtZTogc3RyaW5nKXtcbiAgICAgICAgdGhpcy5lbCgpLmNsYXNzTGlzdC5yZW1vdmUobmFtZSk7XG4gICAgfVxuXG4gICAgdG9nZ2xlQ2xhc3MobmFtZTogc3RyaW5nKXtcbiAgICAgICAgdGhpcy5lbCgpLmNsYXNzTGlzdC50b2dnbGUobmFtZSk7XG4gICAgfVxuXG4gICAgc2hvdygpe1xuICAgICAgICB0aGlzLmVsKCkuc3R5bGUuZGlzcGxheSA9IFwiYmxvY2tcIjtcbiAgICB9XG5cbiAgICBoaWRlKCl7XG4gICAgICAgIHRoaXMuZWwoKS5zdHlsZS5kaXNwbGF5ID0gXCJub25lXCI7XG4gICAgfVxuXG4gICAgYWRkQ2hpbGQobmFtZTogc3RyaW5nLCBjb21wb25lbnQ6IENvbXBvbmVudCwgaW5kZXg6ID9udW1iZXIpIDogdm9pZHtcbiAgICAgICAgbGV0IGxvY2F0aW9uID0gdGhpcy5lbCgpO1xuICAgICAgICBpZighaW5kZXgpe1xuICAgICAgICAgICAgaW5kZXggPSAtMTtcbiAgICAgICAgfVxuXG4gICAgICAgIGlmKHR5cGVvZiBjb21wb25lbnQuZWwgPT09IFwiZnVuY3Rpb25cIiAmJiBjb21wb25lbnQuZWwoKSl7XG4gICAgICAgICAgICBpZihpbmRleCA9PT0gLTEpe1xuICAgICAgICAgICAgICAgIGxvY2F0aW9uLmFwcGVuZENoaWxkKGNvbXBvbmVudC5lbCgpKTtcbiAgICAgICAgICAgIH1lbHNle1xuICAgICAgICAgICAgICAgIGxldCBjaGlsZHJlbiA9IGxvY2F0aW9uLmNoaWxkTm9kZXM7XG4gICAgICAgICAgICAgICAgbGV0IGNoaWxkID0gY2hpbGRyZW5baW5kZXhdO1xuICAgICAgICAgICAgICAgIGxvY2F0aW9uLmluc2VydEJlZm9yZShjb21wb25lbnQuZWwoKSwgY2hpbGQpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG5cbiAgICAgICAgdGhpcy5fY2hpbGRyZW4ucHVzaCh7XG4gICAgICAgICAgICBuYW1lLFxuICAgICAgICAgICAgY29tcG9uZW50LFxuICAgICAgICAgICAgbG9jYXRpb25cbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgcmVtb3ZlQ2hpbGQobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhpcy5fY2hpbGRyZW4gPSB0aGlzLl9jaGlsZHJlbi5yZWR1Y2UoKGFjYywgY29tcG9uZW50KT0+e1xuICAgICAgICAgICAgaWYoY29tcG9uZW50Lm5hbWUgIT09IG5hbWUpe1xuICAgICAgICAgICAgICAgIGFjYy5wdXNoKGNvbXBvbmVudCk7XG4gICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICBjb21wb25lbnQuY29tcG9uZW50LmRpc3Bvc2UoKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHJldHVybiBhY2M7XG4gICAgICAgIH0sIFtdKTtcbiAgICB9XG5cbiAgICBnZXRDaGlsZChuYW1lOiBzdHJpbmcpOiBDb21wb25lbnQgfCBudWxse1xuICAgICAgICBsZXQgY29tcG9uZW50O1xuICAgICAgICBmb3IobGV0IGkgPSAwOyBpIDwgdGhpcy5fY2hpbGRyZW4ubGVuZ3RoOyBpKyspe1xuICAgICAgICAgICAgaWYodGhpcy5fY2hpbGRyZW5baV0ubmFtZSA9PT0gbmFtZSl7XG4gICAgICAgICAgICAgICAgY29tcG9uZW50ID0gdGhpcy5fY2hpbGRyZW5baV07XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGNvbXBvbmVudD8gY29tcG9uZW50LmNvbXBvbmVudDogbnVsbDtcbiAgICB9XG5cbiAgICBnZXQgcGxheWVyKCk6IFBsYXllcntcbiAgICAgICAgcmV0dXJuIHRoaXMuX3BsYXllcjtcbiAgICB9XG5cbiAgICBnZXQgb3B0aW9ucygpOiBhbnkge1xuICAgICAgICByZXR1cm4gdGhpcy5fb3B0aW9ucztcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IENvbXBvbmVudDtcbiIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyLCBTZXR0aW5ncyB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBUd29EVmlkZW8gZnJvbSAnLi9Ud29EVmlkZW8nO1xuaW1wb3J0IFRIUkVFIGZyb20gXCJ0aHJlZVwiO1xuXG5jbGFzcyBEdWFsRmlzaGV5ZSBleHRlbmRzIFR3b0RWaWRlb3tcbiAgICBfbWVzaDogYW55O1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IFNldHRpbmdzLCByZW5kZXJFbGVtZW50OiBIVE1MRWxlbWVudCl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucywgcmVuZGVyRWxlbWVudCk7XG5cbiAgICAgICAgbGV0IGdlb21ldHJ5ID0gbmV3IFRIUkVFLlNwaGVyZUJ1ZmZlckdlb21ldHJ5KCA1MDAsIDYwLCA0MCApLnRvTm9uSW5kZXhlZCgpO1xuICAgICAgICBsZXQgbm9ybWFscyA9IGdlb21ldHJ5LmF0dHJpYnV0ZXMubm9ybWFsLmFycmF5O1xuICAgICAgICBsZXQgdXZzID0gZ2VvbWV0cnkuYXR0cmlidXRlcy51di5hcnJheTtcbiAgICAgICAgbGV0IGwgPSBub3JtYWxzLmxlbmd0aCAvIDM7XG4gICAgICAgIGZvciAoIGxldCBpID0gMDsgaSA8IGwgLyAyOyBpICsrICkge1xuICAgICAgICAgICAgbGV0IHggPSBub3JtYWxzWyBpICogMyArIDAgXTtcbiAgICAgICAgICAgIGxldCB5ID0gbm9ybWFsc1sgaSAqIDMgKyAxIF07XG4gICAgICAgICAgICBsZXQgeiA9IG5vcm1hbHNbIGkgKiAzICsgMiBdO1xuXG4gICAgICAgICAgICBsZXQgciA9ICggeCA9PSAwICYmIHogPT0gMCApID8gMSA6ICggTWF0aC5hY29zKCB5ICkgLyBNYXRoLnNxcnQoIHggKiB4ICsgeiAqIHogKSApICogKCAyIC8gTWF0aC5QSSApO1xuICAgICAgICAgICAgdXZzWyBpICogMiArIDAgXSA9IHggKiB0aGlzLm9wdGlvbnMuZHVhbEZpc2guY2lyY2xlMS5yeCAqIHIgKiB0aGlzLm9wdGlvbnMuZHVhbEZpc2guY2lyY2xlMS5jb3ZlclggICsgdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTEueDtcbiAgICAgICAgICAgIHV2c1sgaSAqIDIgKyAxIF0gPSB6ICogdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTEucnkgKiByICogdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTEuY292ZXJZICArIHRoaXMub3B0aW9ucy5kdWFsRmlzaC5jaXJjbGUxLnk7XG4gICAgICAgIH1cbiAgICAgICAgZm9yICggbGV0IGkgPSBsIC8gMjsgaSA8IGw7IGkgKysgKSB7XG4gICAgICAgICAgICBsZXQgeCA9IG5vcm1hbHNbIGkgKiAzICsgMCBdO1xuICAgICAgICAgICAgbGV0IHkgPSBub3JtYWxzWyBpICogMyArIDEgXTtcbiAgICAgICAgICAgIGxldCB6ID0gbm9ybWFsc1sgaSAqIDMgKyAyIF07XG5cbiAgICAgICAgICAgIGxldCByID0gKCB4ID09IDAgJiYgeiA9PSAwICkgPyAxIDogKCBNYXRoLmFjb3MoIC0geSApIC8gTWF0aC5zcXJ0KCB4ICogeCArIHogKiB6ICkgKSAqICggMiAvIE1hdGguUEkgKTtcbiAgICAgICAgICAgIHV2c1sgaSAqIDIgKyAwIF0gPSAtIHggKiB0aGlzLm9wdGlvbnMuZHVhbEZpc2guY2lyY2xlMi5yeCAqIHIgKiB0aGlzLm9wdGlvbnMuZHVhbEZpc2guY2lyY2xlMi5jb3ZlclggICsgdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTIueDtcbiAgICAgICAgICAgIHV2c1sgaSAqIDIgKyAxIF0gPSB6ICogdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTIucnkgKiByICogdGhpcy5vcHRpb25zLmR1YWxGaXNoLmNpcmNsZTIuY292ZXJZICArIHRoaXMub3B0aW9ucy5kdWFsRmlzaC5jaXJjbGUyLnk7XG4gICAgICAgIH1cbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWCggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVYKTtcbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWSggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVZKTtcbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWiggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVaKTtcbiAgICAgICAgZ2VvbWV0cnkuc2NhbGUoIC0gMSwgMSwgMSApO1xuXG4gICAgICAgIC8vZGVmaW5lIG1lc2hcbiAgICAgICAgdGhpcy5fbWVzaCA9IG5ldyBUSFJFRS5NZXNoKGdlb21ldHJ5LFxuICAgICAgICAgICAgbmV3IFRIUkVFLk1lc2hCYXNpY01hdGVyaWFsKHsgbWFwOiB0aGlzLl90ZXh0dXJlfSlcbiAgICAgICAgKTtcbiAgICAgICAgdGhpcy5fc2NlbmUuYWRkKHRoaXMuX21lc2gpO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgRHVhbEZpc2hleWU7IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIFNldHRpbmdzIH0gZnJvbSAnLi4vdHlwZXMnO1xuaW1wb3J0IFR3b0RWaWRlbyBmcm9tICcuL1R3b0RWaWRlbyc7XG5pbXBvcnQgVEhSRUUgZnJvbSBcInRocmVlXCI7XG5cbmNsYXNzIEVxdWlyZWN0YW5ndWxhciBleHRlbmRzIFR3b0RWaWRlb3tcbiAgICBfbWVzaDogYW55O1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IFNldHRpbmdzLCByZW5kZXJFbGVtZW50OiBIVE1MRWxlbWVudCl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucywgcmVuZGVyRWxlbWVudCk7XG5cbiAgICAgICAgbGV0IGdlb21ldHJ5ID0gbmV3IFRIUkVFLlNwaGVyZUdlb21ldHJ5KDUwMCwgNjAsIDQwKTtcbiAgICAgICAgZ2VvbWV0cnkuc2NhbGUoIC0gMSwgMSwgMSApO1xuICAgICAgICAvL2RlZmluZSBtZXNoXG4gICAgICAgIHRoaXMuX21lc2ggPSBuZXcgVEhSRUUuTWVzaChnZW9tZXRyeSxcbiAgICAgICAgICAgIG5ldyBUSFJFRS5NZXNoQmFzaWNNYXRlcmlhbCh7IG1hcDogdGhpcy5fdGV4dHVyZX0pXG4gICAgICAgICk7XG4gICAgICAgIHRoaXMuX3NjZW5lLmFkZCh0aGlzLl9tZXNoKTtcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IEVxdWlyZWN0YW5ndWxhcjsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdHlwZSB7IFBsYXllciwgU2V0dGluZ3MgfSBmcm9tICcuLi90eXBlcyc7XG5pbXBvcnQgVHdvRFZpZGVvIGZyb20gJy4vVHdvRFZpZGVvJztcbmltcG9ydCBUSFJFRSBmcm9tIFwidGhyZWVcIjtcblxuY2xhc3MgRmlzaGV5ZSBleHRlbmRzIFR3b0RWaWRlb3tcbiAgICBfbWVzaDogYW55O1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IFNldHRpbmdzLCByZW5kZXJFbGVtZW50OiBIVE1MRWxlbWVudCl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucywgcmVuZGVyRWxlbWVudCk7XG5cbiAgICAgICAgbGV0IGdlb21ldHJ5ID0gbmV3IFRIUkVFLlNwaGVyZUJ1ZmZlckdlb21ldHJ5KCA1MDAsIDYwLCA0MCApLnRvTm9uSW5kZXhlZCgpO1xuICAgICAgICBsZXQgbm9ybWFscyA9IGdlb21ldHJ5LmF0dHJpYnV0ZXMubm9ybWFsLmFycmF5O1xuICAgICAgICBsZXQgdXZzID0gZ2VvbWV0cnkuYXR0cmlidXRlcy51di5hcnJheTtcbiAgICAgICAgZm9yICggbGV0IGkgPSAwLCBsID0gbm9ybWFscy5sZW5ndGggLyAzOyBpIDwgbDsgaSArKyApIHtcbiAgICAgICAgICAgIGxldCB4ID0gbm9ybWFsc1sgaSAqIDMgKyAwIF07XG4gICAgICAgICAgICBsZXQgeSA9IG5vcm1hbHNbIGkgKiAzICsgMSBdO1xuICAgICAgICAgICAgbGV0IHogPSBub3JtYWxzWyBpICogMyArIDIgXTtcblxuICAgICAgICAgICAgbGV0IHIgPSBNYXRoLmFzaW4oTWF0aC5zcXJ0KHggKiB4ICsgeiAqIHopIC8gTWF0aC5zcXJ0KHggKiB4ICArIHkgKiB5ICsgeiAqIHopKSAvIE1hdGguUEk7XG4gICAgICAgICAgICBpZih5IDwgMCkgciA9IDEgLSByO1xuICAgICAgICAgICAgbGV0IHRoZXRhID0gKHggPT09IDAgJiYgeiA9PT0gMCk/IDAgOiBNYXRoLmFjb3MoeCAvIE1hdGguc3FydCh4ICogeCArIHogKiB6KSk7XG4gICAgICAgICAgICBpZih6IDwgMCkgdGhldGEgPSB0aGV0YSAqIC0xO1xuICAgICAgICAgICAgdXZzWyBpICogMiArIDAgXSA9IC0wLjggKiByICogTWF0aC5jb3ModGhldGEpICsgMC41O1xuICAgICAgICAgICAgdXZzWyBpICogMiArIDEgXSA9IDAuOCAqIHIgKiBNYXRoLnNpbih0aGV0YSkgKyAwLjU7XG4gICAgICAgIH1cbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWCggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVYKTtcbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWSggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVZKTtcbiAgICAgICAgZ2VvbWV0cnkucm90YXRlWiggdGhpcy5vcHRpb25zLlNwaGVyZS5yb3RhdGVaKTtcbiAgICAgICAgZ2VvbWV0cnkuc2NhbGUoIC0gMSwgMSwgMSApO1xuICAgICAgICAvL2RlZmluZSBtZXNoXG4gICAgICAgIHRoaXMuX21lc2ggPSBuZXcgVEhSRUUuTWVzaChnZW9tZXRyeSxcbiAgICAgICAgICAgIG5ldyBUSFJFRS5NZXNoQmFzaWNNYXRlcmlhbCh7IG1hcDogdGhpcy5fdGV4dHVyZX0pXG4gICAgICAgICk7XG4gICAgICAgIHRoaXMuX3NjZW5lLmFkZCh0aGlzLl9tZXNoKTtcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IEZpc2hleWU7IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIgfSBmcm9tICcuLi90eXBlcyc7XG5pbXBvcnQgQ29tcG9uZW50IGZyb20gJy4vQ29tcG9uZW50JztcblxuY2xhc3MgSGVscGVyQ2FudmFzIGV4dGVuZHMgQ29tcG9uZW50IHtcbiAgICBfdmlkZW9FbGVtZW50OiBIVE1MVmlkZW9FbGVtZW50O1xuICAgIF9jb250ZXh0OiBhbnk7XG4gICAgX3dpZHRoOiBudW1iZXI7XG4gICAgX2hlaWdodDogbnVtYmVyO1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM/OiBhbnkgPSB7fSl7XG4gICAgICAgIGxldCBlbGVtZW50OiBhbnkgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdjYW52YXMnKTtcbiAgICAgICAgZWxlbWVudC5jbGFzc05hbWUgPSBcInZqcy1wYW5vcmFtYS12aWRlby1oZWxwZXItY2FudmFzXCI7XG4gICAgICAgIG9wdGlvbnMuZWwgPSBlbGVtZW50O1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMpO1xuICAgICAgICB0aGlzLl92aWRlb0VsZW1lbnQgPSBwbGF5ZXIuZ2V0VmlkZW9FbCgpO1xuICAgICAgICB0aGlzLl93aWR0aCA9IHRoaXMuX3ZpZGVvRWxlbWVudC5vZmZzZXRXaWR0aDtcbiAgICAgICAgdGhpcy5faGVpZ2h0ID0gdGhpcy5fdmlkZW9FbGVtZW50Lm9mZnNldEhlaWdodDtcblxuICAgICAgICB0aGlzLnVwZGF0ZURpbWVudGlvbigpO1xuICAgICAgICBlbGVtZW50LnN0eWxlLmRpc3BsYXkgPSBcIm5vbmVcIjtcblxuICAgICAgICB0aGlzLl9jb250ZXh0ID0gZWxlbWVudC5nZXRDb250ZXh0KCcyZCcpO1xuICAgICAgICB0aGlzLl9jb250ZXh0LmRyYXdJbWFnZSh0aGlzLl92aWRlb0VsZW1lbnQsIDAsIDAsIHRoaXMuX3dpZHRoLCB0aGlzLl9oZWlnaHQpO1xuICAgICAgICAvKipcbiAgICAgICAgICogR2V0IGFjdHVhbCB2aWRlbyBkaW1lbnNpb24gYWZ0ZXIgdmlkZW8gbG9hZC5cbiAgICAgICAgICovXG4gICAgICAgIHBsYXllci5vbmUoXCJsb2FkZWRtZXRhZGF0YVwiLCAoKSA9PiB7XG4gICAgICAgICAgICB0aGlzLl93aWR0aCA9IHRoaXMuX3ZpZGVvRWxlbWVudC52aWRlb1dpZHRoO1xuICAgICAgICAgICAgdGhpcy5faGVpZ2h0ID0gdGhpcy5fdmlkZW9FbGVtZW50LnZpZGVvSGVpZ2h0O1xuICAgICAgICAgICAgdGhpcy51cGRhdGVEaW1lbnRpb24oKTtcbiAgICAgICAgICAgIHRoaXMucmVuZGVyKCk7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIHVwZGF0ZURpbWVudGlvbigpe1xuICAgICAgICB0aGlzLmVsKCkud2lkdGggPSB0aGlzLl93aWR0aDtcbiAgICAgICAgdGhpcy5lbCgpLmhlaWdodCA9IHRoaXMuX2hlaWdodDtcbiAgICB9XG5cbiAgICBlbCgpe1xuICAgICAgICByZXR1cm4gdGhpcy5fZWw7XG4gICAgfVxuXG4gICAgcmVuZGVyKCl7XG4gICAgICAgIHRoaXMuX2NvbnRleHQuZHJhd0ltYWdlKHRoaXMuX3ZpZGVvRWxlbWVudCwgMCwgMCwgdGhpcy5fd2lkdGgsIHRoaXMuX2hlaWdodCk7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBIZWxwZXJDYW52YXM7IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIE1hcmtlclNldHRpbmdzLCBQb2ludCB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBUSFJFRSBmcm9tIFwidGhyZWVcIjtcbmltcG9ydCBDb21wb25lbnQgZnJvbSAnLi9Db21wb25lbnQnO1xuaW1wb3J0IEJhc2VDYW52YXMgZnJvbSAnLi9CYXNlQ2FudmFzJztcbmltcG9ydCB7IG1lcmdlT3B0aW9ucyB9IGZyb20gJy4uL3V0aWxzJztcblxuY29uc3QgZGVmYXVsdHMgPSB7XG4gICAga2V5UG9pbnQ6IC0xLFxuICAgIGR1cmF0aW9uOiAtMVxufTtcblxuY2xhc3MgTWFya2VyIGV4dGVuZHMgQ29tcG9uZW50e1xuICAgIF9wb3NpdGlvbjogVEhSRUUuVmVjdG9yMztcbiAgICBfZW5hYmxlOiBib29sZWFuO1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IE1hcmtlclNldHRpbmdzICYge1xuICAgICAgICBlbD86IEhUTUxFbGVtZW50O1xuICAgIH0pe1xuICAgICAgICBsZXQgZWw6IEhUTUxFbGVtZW50O1xuXG4gICAgICAgIGxldCBlbGVtID0gb3B0aW9ucy5lbGVtZW50O1xuICAgICAgICBpZih0eXBlb2YgZWxlbSA9PT0gXCJzdHJpbmdcIil7XG4gICAgICAgICAgICBlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO1xuICAgICAgICAgICAgZWwuaW5uZXJUZXh0ID0gZWxlbTtcbiAgICAgICAgfWVsc2Uge1xuICAgICAgICAgICAgZWwgPSBlbGVtO1xuICAgICAgICB9XG4gICAgICAgIGVsLmlkID0gb3B0aW9ucy5pZCB8fCBcIlwiO1xuICAgICAgICBlbC5jbGFzc05hbWUgPSBcInZqcy1tYXJrZXJcIjtcblxuICAgICAgICBvcHRpb25zLmVsID0gZWw7XG5cbiAgICAgICAgc3VwZXIocGxheWVyLCBvcHRpb25zKTtcbiAgICAgICAgdGhpcy5fb3B0aW9ucyA9IG1lcmdlT3B0aW9ucyh7fSwgZGVmYXVsdHMsIG9wdGlvbnMpO1xuXG4gICAgICAgIGxldCBwaGkgPSBUSFJFRS5NYXRoLmRlZ1RvUmFkKCA5MCAtIG9wdGlvbnMubG9jYXRpb24ubGF0ICk7XG4gICAgICAgIGxldCB0aGV0YSA9IFRIUkVFLk1hdGguZGVnVG9SYWQoIG9wdGlvbnMubG9jYXRpb24ubG9uICk7XG4gICAgICAgIHRoaXMuX3Bvc2l0aW9uID0gbmV3IFRIUkVFLlZlY3RvcjMoXG4gICAgICAgICAgICBvcHRpb25zLnJhZGl1cyAqIE1hdGguc2luKCBwaGkgKSAqIE1hdGguY29zKCB0aGV0YSApLFxuICAgICAgICAgICAgb3B0aW9ucy5yYWRpdXMgKiBNYXRoLmNvcyggcGhpICksXG4gICAgICAgICAgICBvcHRpb25zLnJhZGl1cyAqIE1hdGguc2luKCBwaGkgKSAqIE1hdGguc2luKCB0aGV0YSApLFxuICAgICAgICApO1xuICAgICAgICBpZih0aGlzLm9wdGlvbnMua2V5UG9pbnQgPCAwKXtcbiAgICAgICAgICAgIHRoaXMuZW5hYmxlTWFya2VyKCk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBlbmFibGVNYXJrZXIoKXtcbiAgICAgICAgdGhpcy5fZW5hYmxlID0gdHJ1ZTtcbiAgICAgICAgdGhpcy5hZGRDbGFzcyhcInZqcy1tYXJrZXItLWVuYWJsZVwiKTtcbiAgICAgICAgaWYodGhpcy5vcHRpb25zLm9uU2hvdyl7XG4gICAgICAgICAgICB0aGlzLm9wdGlvbnMub25TaG93LmNhbGwobnVsbCk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBkaXNhYmxlTWFya2VyKCl7XG4gICAgICAgIHRoaXMuX2VuYWJsZSA9IGZhbHNlO1xuICAgICAgICB0aGlzLnJlbW92ZUNsYXNzKFwidmpzLW1hcmtlci0tZW5hYmxlXCIpO1xuICAgICAgICBpZih0aGlzLm9wdGlvbnMub25IaWRlKXtcbiAgICAgICAgICAgIHRoaXMub3B0aW9ucy5vbkhpZGUuY2FsbChudWxsKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIHJlbmRlcihjYW52YXM6IEJhc2VDYW52YXMsIGNhbWVyYTogVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmEpe1xuICAgICAgICBsZXQgYW5nbGUgPSB0aGlzLl9wb3NpdGlvbi5hbmdsZVRvKGNhbWVyYS50YXJnZXQpO1xuICAgICAgICBpZihhbmdsZSA+IE1hdGguUEkgKiAwLjQpe1xuICAgICAgICAgICAgdGhpcy5hZGRDbGFzcyhcInZqcy1tYXJrZXItLWJhY2tzaWRlXCIpO1xuICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgIHRoaXMucmVtb3ZlQ2xhc3MoXCJ2anMtbWFya2VyLS1iYWNrc2lkZVwiKTtcbiAgICAgICAgICAgIGxldCB2ZWN0b3IgPSB0aGlzLl9wb3NpdGlvbi5jbG9uZSgpLnByb2plY3QoY2FtZXJhKTtcbiAgICAgICAgICAgIGxldCB3aWR0aCA9IGNhbnZhcy5WUk1vZGU/IGNhbnZhcy5fd2lkdGggLyAyOiBjYW52YXMuX3dpZHRoO1xuICAgICAgICAgICAgbGV0IHBvaW50OiBQb2ludCA9IHtcbiAgICAgICAgICAgICAgICB4OiAodmVjdG9yLnggKyAxKSAvIDIgKiB3aWR0aCxcbiAgICAgICAgICAgICAgICB5OiAtICh2ZWN0b3IueSAtIDEpIC8gMiAqIGNhbnZhcy5faGVpZ2h0XG4gICAgICAgICAgICB9O1xuICAgICAgICAgICAgdGhpcy5lbCgpLnN0eWxlLnRyYW5zZm9ybSA9IGB0cmFuc2xhdGUoJHtwb2ludC54fXB4LCAke3BvaW50Lnl9cHgpYDtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGdldCBlbmFibGUoKTogYm9vbGVhbntcbiAgICAgICAgcmV0dXJuIHRoaXMuX2VuYWJsZTtcbiAgICB9XG5cbiAgICBnZXQgcG9zaXRpb24oKTogVEhSRUUuVmVjdG9yM3tcbiAgICAgICAgcmV0dXJuIHRoaXMuX3Bvc2l0aW9uO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgTWFya2VyOyIsIi8vIEBmbG93XG5cbmltcG9ydCBCYXNlQ2FudmFzIGZyb20gJy4vQmFzZUNhbnZhcyc7XG5pbXBvcnQgQ29tcG9uZW50IGZyb20gJy4vQ29tcG9uZW50JztcbmltcG9ydCBNYXJrZXJHcm91cCBmcm9tICcuL01hcmtlckdyb3VwJztcbmltcG9ydCB7IG1lcmdlT3B0aW9ucyB9IGZyb20gJy4uL3V0aWxzJztcbmltcG9ydCB0eXBlIHsgUGxheWVyLCBNYXJrZXJTZXR0aW5ncyB9IGZyb20gJy4uL3R5cGVzJztcblxuY2xhc3MgTWFya2VyQ29udGFpbmVyIGV4dGVuZHMgQ29tcG9uZW50e1xuICAgIF9jYW52YXM6IEJhc2VDYW52YXM7XG5cbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczoge1xuICAgICAgICBjYW52YXM6IEJhc2VDYW52YXM7XG4gICAgICAgIG1hcmtlcnM6IE1hcmtlclNldHRpbmdzW107XG4gICAgICAgIFZSRW5hYmxlOiBib29sZWFuO1xuICAgIH0pe1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMpO1xuICAgICAgICB0aGlzLmVsKCkuY2xhc3NMaXN0LmFkZChcInZqcy1tYXJrZXItY29udGFpbmVyXCIpO1xuICAgICAgICB0aGlzLl9jYW52YXMgPSB0aGlzLm9wdGlvbnMuY2FudmFzO1xuXG4gICAgICAgIGlmKHRoaXMub3B0aW9ucy5WUkVuYWJsZSl7XG4gICAgICAgICAgICBsZXQgbGVmdE1hcmtlckdyb3VwID0gbmV3IE1hcmtlckdyb3VwKHRoaXMucGxheWVyLCB7XG4gICAgICAgICAgICAgICAgaWQ6IFwibGVmdF9ncm91cFwiLFxuICAgICAgICAgICAgICAgIGNhbnZhczogdGhpcy5fY2FudmFzLFxuICAgICAgICAgICAgICAgIG1hcmtlcnM6IHRoaXMub3B0aW9ucy5tYXJrZXJzLFxuICAgICAgICAgICAgICAgIGNhbWVyYTogdGhpcy5fY2FudmFzLl9jYW1lcmFcbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgICAgICBsZXQgbWFya2Vyc1NldHRpbmdzID0gdGhpcy5vcHRpb25zLm1hcmtlcnMubWFwKChtYXJrZXI6IE1hcmtlclNldHRpbmdzKT0+e1xuICAgICAgICAgICAgICAgIGxldCBuZXdNYXJrZXIgPSBtZXJnZU9wdGlvbnMoe30sIG1hcmtlcik7XG4gICAgICAgICAgICAgICAgbmV3TWFya2VyLm9uU2hvdyA9IHVuZGVmaW5lZDtcbiAgICAgICAgICAgICAgICBuZXdNYXJrZXIub25IaWRlID0gdW5kZWZpbmVkO1xuICAgICAgICAgICAgICAgIHJldHVybiBuZXdNYXJrZXI7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIGxldCByaWdodE1hcmtlckdyb3VwID0gbmV3IE1hcmtlckdyb3VwKHRoaXMucGxheWVyLCB7XG4gICAgICAgICAgICAgICAgaWQ6IFwicmlnaHRfZ3JvdXBcIixcbiAgICAgICAgICAgICAgICBjYW52YXM6IHRoaXMuX2NhbnZhcyxcbiAgICAgICAgICAgICAgICBtYXJrZXJzOiBtYXJrZXJzU2V0dGluZ3MsXG4gICAgICAgICAgICAgICAgY2FtZXJhOiB0aGlzLl9jYW52YXMuX2NhbWVyYVxuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB0aGlzLmFkZENoaWxkKFwibGVmdE1hcmtlckdyb3VwXCIsIGxlZnRNYXJrZXJHcm91cCk7XG4gICAgICAgICAgICB0aGlzLmFkZENoaWxkKFwicmlnaHRNYXJrZXJHcm91cFwiLCByaWdodE1hcmtlckdyb3VwKTtcblxuICAgICAgICAgICAgbGVmdE1hcmtlckdyb3VwLmF0dGFjaEV2ZW50cygpO1xuICAgICAgICAgICAgaWYodGhpcy5fY2FudmFzLlZSTW9kZSl7XG4gICAgICAgICAgICAgICAgcmlnaHRNYXJrZXJHcm91cC5hdHRhY2hFdmVudHMoKTtcbiAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgdGhpcy5wbGF5ZXIub24oXCJWUk1vZGVPblwiLCAoKT0+e1xuICAgICAgICAgICAgICAgIHRoaXMuZWwoKS5jbGFzc0xpc3QuYWRkKFwidmpzLW1hcmtlci1jb250YWluZXItLVZSRW5hYmxlXCIpO1xuICAgICAgICAgICAgICAgIGxlZnRNYXJrZXJHcm91cC5jYW1lcmEgPSB0aGlzLl9jYW52YXMuX2NhbWVyYUw7XG4gICAgICAgICAgICAgICAgcmlnaHRNYXJrZXJHcm91cC5jYW1lcmEgPSB0aGlzLl9jYW52YXMuX2NhbWVyYVI7XG4gICAgICAgICAgICAgICAgcmlnaHRNYXJrZXJHcm91cC5hdHRhY2hFdmVudHMoKTtcbiAgICAgICAgICAgIH0pO1xuXG4gICAgICAgICAgICB0aGlzLnBsYXllci5vbihcIlZSTW9kZU9mZlwiLCAoKT0+e1xuICAgICAgICAgICAgICAgIHRoaXMuZWwoKS5jbGFzc0xpc3QucmVtb3ZlKFwidmpzLW1hcmtlci1jb250YWluZXItLVZSRW5hYmxlXCIpO1xuICAgICAgICAgICAgICAgIGxlZnRNYXJrZXJHcm91cC5jYW1lcmEgPSB0aGlzLl9jYW52YXMuX2NhbWVyYTtcbiAgICAgICAgICAgICAgICByaWdodE1hcmtlckdyb3VwLmRldGFjaEV2ZW50cygpO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgIH1lbHNle1xuICAgICAgICAgICAgbGV0IG1hcmtlckdyb3VwID0gbmV3IE1hcmtlckdyb3VwKHRoaXMucGxheWVyLCB7XG4gICAgICAgICAgICAgICAgaWQ6IFwiZ3JvdXBcIixcbiAgICAgICAgICAgICAgICBjYW52YXM6IHRoaXMuX2NhbnZhcyxcbiAgICAgICAgICAgICAgICBtYXJrZXJzOiB0aGlzLm9wdGlvbnMubWFya2VycyxcbiAgICAgICAgICAgICAgICBjYW1lcmE6IHRoaXMuX2NhbnZhcy5fY2FtZXJhXG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIHRoaXMuYWRkQ2hpbGQoXCJtYXJrZXJHcm91cFwiLCBtYXJrZXJHcm91cCk7XG4gICAgICAgICAgICBtYXJrZXJHcm91cC5hdHRhY2hFdmVudHMoKTtcbiAgICAgICAgfVxuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgTWFya2VyQ29udGFpbmVyO1xuIiwiLy8gQGZsb3dcblxuaW1wb3J0IFRIUkVFIGZyb20gXCJ0aHJlZVwiO1xuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIE1hcmtlclNldHRpbmdzIH0gZnJvbSAnLi4vdHlwZXMnO1xuaW1wb3J0IENvbXBvbmVudCBmcm9tICcuL0NvbXBvbmVudCc7XG5pbXBvcnQgQmFzZUNhbnZhcyBmcm9tICcuL0Jhc2VDYW52YXMnO1xuaW1wb3J0IE1hcmtlciBmcm9tICcuL01hcmtlcic7XG5cbmNsYXNzIE1hcmtlckdyb3VwIGV4dGVuZHMgQ29tcG9uZW50e1xuICAgIC8vc2F2ZSB0b3RhbCBtYXJrZXJzIGVuYWJsZSB0byBnZW5lcmF0ZSBtYXJrZXIgaWRcbiAgICBfdG90YWxNYXJrZXJzOiBudW1iZXI7XG4gICAgX21hcmtlcnM6IE1hcmtlcltdO1xuICAgIF9jYW1lcmE6IFRIUkVFLlBlcnNwZWN0aXZlQ2FtZXJhO1xuICAgIF9jYW52YXM6IEJhc2VDYW52YXM7XG5cbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczoge1xuICAgICAgICBpZDogc3RyaW5nO1xuICAgICAgICBtYXJrZXJzOiBNYXJrZXJTZXR0aW5nc1tdLFxuICAgICAgICBjYW52YXM6IEJhc2VDYW52YXMsXG4gICAgICAgIGNhbWVyYTogVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmFcbiAgICB9KXtcbiAgICAgICAgc3VwZXIocGxheWVyLCBvcHRpb25zKTtcbiAgICAgICAgdGhpcy5fdG90YWxNYXJrZXJzID0gMDtcbiAgICAgICAgdGhpcy5fbWFya2VycyA9IFtdO1xuICAgICAgICB0aGlzLl9jYW1lcmEgPSBvcHRpb25zLmNhbWVyYTtcbiAgICAgICAgdGhpcy5lbCgpLmNsYXNzTGlzdC5hZGQoXCJ2anMtbWFya2VyLWdyb3VwXCIpO1xuICAgICAgICB0aGlzLl9jYW52YXMgPSBvcHRpb25zLmNhbnZhcztcblxuICAgICAgICB0aGlzLm9wdGlvbnMubWFya2Vycy5mb3JFYWNoKChtYXJrU2V0dGluZyk9PntcbiAgICAgICAgICAgIHRoaXMuYWRkTWFya2VyKG1hcmtTZXR0aW5nKTtcbiAgICAgICAgfSk7XG5cbiAgICAgICAgdGhpcy5yZW5kZXJNYXJrZXJzKCk7XG4gICAgfVxuXG4gICAgYXR0YWNoRXZlbnRzKCl7XG4gICAgICAgIHRoaXMuZWwoKS5jbGFzc0xpc3QuYWRkKFwidmpzLW1hcmtlci1ncm91cC0tZW5hYmxlXCIpO1xuICAgICAgICB0aGlzLnBsYXllci5vbihcInRpbWV1cGRhdGVcIiwgdGhpcy51cGRhdGVNYXJrZXJzLmJpbmQodGhpcykpO1xuICAgICAgICB0aGlzLl9jYW52YXMuYWRkTGlzdGVuZXIoXCJyZW5kZXJcIiwgdGhpcy5yZW5kZXJNYXJrZXJzLmJpbmQodGhpcykpO1xuICAgIH1cblxuICAgIGRldGFjaEV2ZW50cygpe1xuICAgICAgICB0aGlzLmVsKCkuY2xhc3NMaXN0LnJlbW92ZShcInZqcy1tYXJrZXItZ3JvdXAtLWVuYWJsZVwiKTtcbiAgICAgICAgdGhpcy5wbGF5ZXIub2ZmKFwidGltZXVwZGF0ZVwiLCB0aGlzLnVwZGF0ZU1hcmtlcnMuYmluZCh0aGlzKSk7XG4gICAgICAgIHRoaXMuX2NhbnZhcy5yZW1vdmVMaXN0ZW5lcihcInJlbmRlclwiLCB0aGlzLnJlbmRlck1hcmtlcnMuYmluZCh0aGlzKSk7XG4gICAgfVxuXG4gICAgYWRkTWFya2VyKG1hcmtTZXR0aW5nOiBhbnkpOiBNYXJrZXJ7XG4gICAgICAgIHRoaXMuX3RvdGFsTWFya2VycysrO1xuICAgICAgICBtYXJrU2V0dGluZy5pZD0gYCR7dGhpcy5vcHRpb25zLmlkfV9gICsgKG1hcmtTZXR0aW5nLmlkPyBtYXJrU2V0dGluZy5pZCA6IGBtYXJrZXJfJHt0aGlzLl90b3RhbE1hcmtlcnN9YCk7XG4gICAgICAgIGxldCBtYXJrZXIgPSBuZXcgTWFya2VyKHRoaXMucGxheWVyLCBtYXJrU2V0dGluZyk7XG4gICAgICAgIHRoaXMuYWRkQ2hpbGQobWFya1NldHRpbmcuaWQsIG1hcmtlcik7XG4gICAgICAgIHRoaXMuX21hcmtlcnMucHVzaChtYXJrZXIpO1xuICAgICAgICByZXR1cm4gbWFya2VyO1xuICAgIH1cblxuICAgIHJlbW92ZU1hcmtlcihtYXJrZXJJZDogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhpcy5yZW1vdmVDaGlsZChtYXJrZXJJZCk7XG4gICAgfVxuXG4gICAgdXBkYXRlTWFya2Vycygpe1xuICAgICAgICBsZXQgY3VycmVudFRpbWUgPSB0aGlzLnBsYXllci5nZXRWaWRlb0VsKCkuY3VycmVudFRpbWUgKiAxMDAwO1xuICAgICAgICB0aGlzLl9tYXJrZXJzLmZvckVhY2goKG1hcmtlcik9PntcbiAgICAgICAgICAgIC8vb25seSBjaGVjayBrZXlwb2ludCBncmVhdGVyIGFuZCBlcXVhbCB6ZXJvXG4gICAgICAgICAgICBpZihtYXJrZXIub3B0aW9ucy5rZXlQb2ludCA+PSAwKXtcbiAgICAgICAgICAgICAgICBpZihtYXJrZXIub3B0aW9ucy5kdXJhdGlvbiA+IDApe1xuICAgICAgICAgICAgICAgICAgICAobWFya2VyLm9wdGlvbnMua2V5UG9pbnQgPD0gY3VycmVudFRpbWUgJiYgY3VycmVudFRpbWUgPCBtYXJrZXIub3B0aW9ucy5rZXlQb2ludCArIG1hcmtlci5vcHRpb25zLmR1cmF0aW9uKT9cbiAgICAgICAgICAgICAgICAgICAgICAgICFtYXJrZXIuZW5hYmxlICYmIG1hcmtlci5lbmFibGVNYXJrZXIoKSA6IG1hcmtlci5lbmFibGUgJiYgbWFya2VyLmRpc2FibGVNYXJrZXIoKTtcbiAgICAgICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICAgICAgKG1hcmtlci5vcHRpb25zLmtleVBvaW50IDw9IGN1cnJlbnRUaW1lKT9cbiAgICAgICAgICAgICAgICAgICAgICAgICFtYXJrZXIuZW5hYmxlICYmIG1hcmtlci5lbmFibGVNYXJrZXIoKSA6IG1hcmtlci5lbmFibGUgJiYgbWFya2VyLmRpc2FibGVNYXJrZXIoKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIHJlbmRlck1hcmtlcnMoKXtcbiAgICAgICAgdGhpcy5fbWFya2Vycy5mb3JFYWNoKChtYXJrZXIpPT57XG4gICAgICAgICAgICBpZihtYXJrZXIuZW5hYmxlKXtcbiAgICAgICAgICAgICAgICBtYXJrZXIucmVuZGVyKHRoaXMuX2NhbnZhcywgdGhpcy5fY2FtZXJhKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgc2V0IGNhbWVyYShjYW1lcmE6IFRIUkVFLlBlcnNwZWN0aXZlQ2FtZXJhKXtcbiAgICAgICAgdGhpcy5fY2FtZXJhID0gY2FtZXJhO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgTWFya2VyR3JvdXA7IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIgfSBmcm9tICcuLi90eXBlcyc7XG5pbXBvcnQgQ29tcG9uZW50IGZyb20gJy4vQ29tcG9uZW50JztcblxuY2xhc3MgTm90aWZpY2F0aW9uIGV4dGVuZHMgQ29tcG9uZW50e1xuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiB7XG4gICAgICAgIE1lc3NhZ2U6IHN0cmluZyB8IEhUTUxFbGVtZW50O1xuICAgICAgICBlbD86IEhUTUxFbGVtZW50O1xuICAgIH0pe1xuICAgICAgICBsZXQgZWw6IEhUTUxFbGVtZW50O1xuXG4gICAgICAgIGxldCBtZXNzYWdlID0gb3B0aW9ucy5NZXNzYWdlO1xuICAgICAgICBpZih0eXBlb2YgbWVzc2FnZSA9PT0gJ3N0cmluZycpe1xuICAgICAgICAgICAgZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtcbiAgICAgICAgICAgIGVsLmNsYXNzTmFtZSA9IFwidmpzLXZpZGVvLW5vdGljZS1sYWJlbCB2anMtdmlkZW8tbm90aWNlLXNob3dcIjtcbiAgICAgICAgICAgIGVsLmlubmVyVGV4dCA9IG1lc3NhZ2U7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBlbCA9IG1lc3NhZ2U7XG4gICAgICAgICAgICBlbC5jbGFzc0xpc3QuYWRkKFwidmpzLXZpZGVvLW5vdGljZS1zaG93XCIpO1xuICAgICAgICB9XG5cbiAgICAgICAgb3B0aW9ucy5lbCA9IGVsO1xuXG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucyk7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBOb3RpZmljYXRpb247IiwiLy8gQGZsb3dcblxuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIFNldHRpbmdzIH0gZnJvbSAnLi4vdHlwZXMnO1xuaW1wb3J0IEJhc2VDYW52YXMgZnJvbSAnLi9CYXNlQ2FudmFzJztcbmltcG9ydCBUSFJFRSBmcm9tIFwidGhyZWVcIjtcblxuY2xhc3MgVGhyZWVEVmlkZW8gZXh0ZW5kcyBCYXNlQ2FudmFze1xuICAgIF9jYW1lcmFMOiBhbnk7XG4gICAgX2NhbWVyYVI6IGFueTtcblxuICAgIF9tZXNoTDogYW55O1xuICAgIF9tZXNoUjogYW55O1xuXG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IFNldHRpbmdzLCByZW5kZXJFbGVtZW50OiBIVE1MRWxlbWVudCl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucywgcmVuZGVyRWxlbWVudCk7XG5cbiAgICAgICAgLy9vbmx5IHNob3cgbGVmdCBwYXJ0IGJ5IGRlZmF1bHRcbiAgICAgICAgdGhpcy5fc2NlbmUgPSBuZXcgVEhSRUUuU2NlbmUoKTtcblxuICAgICAgICBsZXQgYXNwZWN0UmF0aW8gPSB0aGlzLl93aWR0aCAvIHRoaXMuX2hlaWdodDtcbiAgICAgICAgLy9kZWZpbmUgY2FtZXJhXG4gICAgICAgIHRoaXMuX2NhbWVyYUwgPSBuZXcgVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmEodGhpcy5vcHRpb25zLmluaXRGb3YsIGFzcGVjdFJhdGlvLCAxLCAyMDAwKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhTC50YXJnZXQgPSBuZXcgVEhSRUUuVmVjdG9yMyggMCwgMCwgMCApO1xuXG4gICAgICAgIHRoaXMuX2NhbWVyYVIgPSBuZXcgVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmEodGhpcy5vcHRpb25zLmluaXRGb3YsIGFzcGVjdFJhdGlvIC8gMiwgMSwgMjAwMCk7XG4gICAgICAgIHRoaXMuX2NhbWVyYVIucG9zaXRpb24uc2V0KCAxMDAwLCAwLCAwICk7XG4gICAgICAgIHRoaXMuX2NhbWVyYVIudGFyZ2V0ID0gbmV3IFRIUkVFLlZlY3RvcjMoIDEwMDAsIDAsIDAgKTtcbiAgICB9XG5cbiAgICBoYW5kbGVSZXNpemUoKTogdm9pZHtcbiAgICAgICAgc3VwZXIuaGFuZGxlUmVzaXplKCk7XG5cbiAgICAgICAgbGV0IGFzcGVjdFJhdGlvID0gdGhpcy5fd2lkdGggLyB0aGlzLl9oZWlnaHQ7XG4gICAgICAgIGlmKCF0aGlzLlZSTW9kZSkge1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhTC5hc3BlY3QgPSBhc3BlY3RSYXRpbztcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwudXBkYXRlUHJvamVjdGlvbk1hdHJpeCgpO1xuICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgIGFzcGVjdFJhdGlvIC89IDI7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFMLmFzcGVjdCA9IGFzcGVjdFJhdGlvO1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi5hc3BlY3QgPSBhc3BlY3RSYXRpbztcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwudXBkYXRlUHJvamVjdGlvbk1hdHJpeCgpO1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi51cGRhdGVQcm9qZWN0aW9uTWF0cml4KCk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBoYW5kbGVNb3VzZVdoZWVsKGV2ZW50OiBhbnkpe1xuICAgICAgICBzdXBlci5oYW5kbGVNb3VzZVdoZWVsKGV2ZW50KTtcblxuICAgICAgICAvLyBXZWJLaXRcbiAgICAgICAgaWYgKCBldmVudC53aGVlbERlbHRhWSApIHtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwuZm92IC09IGV2ZW50LndoZWVsRGVsdGFZICogMC4wNTtcbiAgICAgICAgICAgIC8vIE9wZXJhIC8gRXhwbG9yZXIgOVxuICAgICAgICB9IGVsc2UgaWYgKCBldmVudC53aGVlbERlbHRhICkge1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhTC5mb3YgLT0gZXZlbnQud2hlZWxEZWx0YSAqIDAuMDU7XG4gICAgICAgICAgICAvLyBGaXJlZm94XG4gICAgICAgIH0gZWxzZSBpZiAoIGV2ZW50LmRldGFpbCApIHtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwuZm92ICs9IGV2ZW50LmRldGFpbCAqIDEuMDtcbiAgICAgICAgfVxuICAgICAgICB0aGlzLl9jYW1lcmFMLmZvdiA9IE1hdGgubWluKHRoaXMub3B0aW9ucy5tYXhGb3YsIHRoaXMuX2NhbWVyYUwuZm92KTtcbiAgICAgICAgdGhpcy5fY2FtZXJhTC5mb3YgPSBNYXRoLm1heCh0aGlzLm9wdGlvbnMubWluRm92LCB0aGlzLl9jYW1lcmFMLmZvdik7XG4gICAgICAgIHRoaXMuX2NhbWVyYUwudXBkYXRlUHJvamVjdGlvbk1hdHJpeCgpO1xuICAgICAgICBpZih0aGlzLlZSTW9kZSl7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFSLmZvdiA9IHRoaXMuX2NhbWVyYUwuZm92O1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi51cGRhdGVQcm9qZWN0aW9uTWF0cml4KCk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBlbmFibGVWUigpIHtcbiAgICAgICAgc3VwZXIuZW5hYmxlVlIoKTtcbiAgICAgICAgdGhpcy5fc2NlbmUuYWRkKHRoaXMuX21lc2hSKTtcbiAgICAgICAgdGhpcy5oYW5kbGVSZXNpemUoKTtcbiAgICB9XG5cbiAgICBkaXNhYmxlVlIoKSB7XG4gICAgICAgIHN1cGVyLmRpc2FibGVWUigpO1xuICAgICAgICB0aGlzLl9zY2VuZS5yZW1vdmUodGhpcy5fbWVzaFIpO1xuICAgICAgICB0aGlzLmhhbmRsZVJlc2l6ZSgpO1xuICAgIH1cblxuICAgIHJlbmRlcigpe1xuICAgICAgICBzdXBlci5yZW5kZXIoKTtcblxuICAgICAgICB0aGlzLl9jYW1lcmFMLnRhcmdldC54ID0gNTAwICogTWF0aC5zaW4oIHRoaXMuX3BoaSApICogTWF0aC5jb3MoIHRoaXMuX3RoZXRhICk7XG4gICAgICAgIHRoaXMuX2NhbWVyYUwudGFyZ2V0LnkgPSA1MDAgKiBNYXRoLmNvcyggdGhpcy5fcGhpICk7XG4gICAgICAgIHRoaXMuX2NhbWVyYUwudGFyZ2V0LnogPSA1MDAgKiBNYXRoLnNpbiggdGhpcy5fcGhpICkgKiBNYXRoLnNpbiggdGhpcy5fdGhldGEgKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhTC5sb29rQXQodGhpcy5fY2FtZXJhTC50YXJnZXQpO1xuXG4gICAgICAgIGlmKHRoaXMuVlJNb2RlKXtcbiAgICAgICAgICAgIGxldCB2aWV3UG9ydFdpZHRoID0gdGhpcy5fd2lkdGggLyAyLCB2aWV3UG9ydEhlaWdodCA9IHRoaXMuX2hlaWdodDtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYVIudGFyZ2V0LnggPSAxMDAwICsgNTAwICogTWF0aC5zaW4oIHRoaXMuX3BoaSApICogTWF0aC5jb3MoIHRoaXMuX3RoZXRhICk7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFSLnRhcmdldC55ID0gNTAwICogTWF0aC5jb3MoIHRoaXMuX3BoaSApO1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi50YXJnZXQueiA9IDUwMCAqIE1hdGguc2luKCB0aGlzLl9waGkgKSAqIE1hdGguc2luKCB0aGlzLl90aGV0YSApO1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi5sb29rQXQoIHRoaXMuX2NhbWVyYVIudGFyZ2V0ICk7XG5cbiAgICAgICAgICAgIC8vIHJlbmRlciBsZWZ0IGV5ZVxuICAgICAgICAgICAgdGhpcy5fcmVuZGVyZXIuc2V0Vmlld3BvcnQoIDAsIDAsIHZpZXdQb3J0V2lkdGgsIHZpZXdQb3J0SGVpZ2h0ICk7XG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRTY2lzc29yKCAwLCAwLCB2aWV3UG9ydFdpZHRoLCB2aWV3UG9ydEhlaWdodCApO1xuICAgICAgICAgICAgdGhpcy5fcmVuZGVyZXIucmVuZGVyKCB0aGlzLl9zY2VuZSwgdGhpcy5fY2FtZXJhTCApO1xuXG4gICAgICAgICAgICAvLyByZW5kZXIgcmlnaHQgZXllXG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRWaWV3cG9ydCggdmlld1BvcnRXaWR0aCwgMCwgdmlld1BvcnRXaWR0aCwgdmlld1BvcnRIZWlnaHQgKTtcbiAgICAgICAgICAgIHRoaXMuX3JlbmRlcmVyLnNldFNjaXNzb3IoIHZpZXdQb3J0V2lkdGgsIDAsIHZpZXdQb3J0V2lkdGgsIHZpZXdQb3J0SGVpZ2h0ICk7XG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5yZW5kZXIoIHRoaXMuX3NjZW5lLCB0aGlzLl9jYW1lcmFSICk7XG4gICAgICAgIH1lbHNle1xuICAgICAgICAgICAgdGhpcy5fcmVuZGVyZXIucmVuZGVyKCB0aGlzLl9zY2VuZSwgdGhpcy5fY2FtZXJhTCApO1xuICAgICAgICB9XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBUaHJlZURWaWRlbzsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdHlwZSB7IFBsYXllciB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBDb21wb25lbnQgZnJvbSAnLi9Db21wb25lbnQnO1xuXG5jbGFzcyBUaHVtYm5haWwgZXh0ZW5kcyBDb21wb25lbnR7XG4gICAgY29uc3RydWN0b3IocGxheWVyOiBQbGF5ZXIsIG9wdGlvbnM6IHtcbiAgICAgICAgcG9zdGVyU3JjOiBzdHJpbmc7XG4gICAgICAgIG9uQ29tcGxldGU/OiBGdW5jdGlvbjtcbiAgICAgICAgZWw/OiBIVE1MRWxlbWVudDtcbiAgICB9KXtcbiAgICAgICAgbGV0IGVsOiBIVE1MRWxlbWVudDtcblxuICAgICAgICBlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2ltZycpO1xuICAgICAgICBlbC5zcmMgPSBvcHRpb25zLnBvc3RlclNyYztcblxuICAgICAgICBvcHRpb25zLmVsID0gZWw7XG5cbiAgICAgICAgc3VwZXIocGxheWVyLCBvcHRpb25zKTtcblxuICAgICAgICB0aGlzLm9uZSgnbG9hZCcsICgpPT57XG4gICAgICAgICAgICBpZihvcHRpb25zLm9uQ29tcGxldGUpe1xuICAgICAgICAgICAgICAgIG9wdGlvbnMub25Db21wbGV0ZSgpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KVxuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgVGh1bWJuYWlsOyIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyLCBTZXR0aW5ncyB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBCYXNlQ2FudmFzIGZyb20gJy4vQmFzZUNhbnZhcyc7XG5pbXBvcnQgVEhSRUUgZnJvbSBcInRocmVlXCI7XG5pbXBvcnQgeyBnZXRUb3VjaGVzRGlzdGFuY2UsIGZvdlRvUHJvamVjdGlvbiB9IGZyb20gJy4uL3V0aWxzJ1xuXG5jbGFzcyBUd29EVmlkZW8gZXh0ZW5kcyBCYXNlQ2FudmFze1xuICAgIF9jYW1lcmE6IGFueTtcblxuICAgIF9leWVGT1ZMOiBhbnk7XG4gICAgX2V5ZUZPVlI6IGFueTtcblxuICAgIF9jYW1lcmFMOiBhbnk7XG4gICAgX2NhbWVyYVI6IGFueTtcblxuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBTZXR0aW5ncywgcmVuZGVyRWxlbWVudDogSFRNTEVsZW1lbnQpe1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMsIHJlbmRlckVsZW1lbnQpO1xuXG4gICAgICAgIC8vZGVmaW5lIHNjZW5lXG4gICAgICAgIHRoaXMuX3NjZW5lID0gbmV3IFRIUkVFLlNjZW5lKCk7XG4gICAgICAgIC8vZGVmaW5lIGNhbWVyYVxuICAgICAgICB0aGlzLl9jYW1lcmEgPSBuZXcgVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmEodGhpcy5vcHRpb25zLmluaXRGb3YsIHRoaXMuX3dpZHRoIC8gdGhpcy5faGVpZ2h0LCAxLCAyMDAwKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhLnRhcmdldCA9IG5ldyBUSFJFRS5WZWN0b3IzKCAwLCAwLCAwICk7XG4gICAgfVxuXG4gICAgZW5hYmxlVlIoKXtcbiAgICAgICAgc3VwZXIuZW5hYmxlVlIoKTtcblxuICAgICAgICBpZih0eXBlb2Ygd2luZG93LnZySE1EICE9PSAndW5kZWZpbmVkJyl7XG4gICAgICAgICAgICBsZXQgZXllUGFyYW1zTCA9IHdpbmRvdy52ckhNRC5nZXRFeWVQYXJhbWV0ZXJzKCAnbGVmdCcgKTtcbiAgICAgICAgICAgIGxldCBleWVQYXJhbXNSID0gd2luZG93LnZySE1ELmdldEV5ZVBhcmFtZXRlcnMoICdyaWdodCcgKTtcblxuICAgICAgICAgICAgdGhpcy5fZXllRk9WTCA9IGV5ZVBhcmFtc0wucmVjb21tZW5kZWRGaWVsZE9mVmlldztcbiAgICAgICAgICAgIHRoaXMuX2V5ZUZPVlIgPSBleWVQYXJhbXNSLnJlY29tbWVuZGVkRmllbGRPZlZpZXc7XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLl9jYW1lcmFMID0gbmV3IFRIUkVFLlBlcnNwZWN0aXZlQ2FtZXJhKHRoaXMuX2NhbWVyYS5mb3YsIHRoaXMuX3dpZHRoIC8gMiAvIHRoaXMuX2hlaWdodCwgMSwgMjAwMCk7XG4gICAgICAgIHRoaXMuX2NhbWVyYVIgPSBuZXcgVEhSRUUuUGVyc3BlY3RpdmVDYW1lcmEodGhpcy5fY2FtZXJhLmZvdiwgdGhpcy5fd2lkdGggLyAyIC8gdGhpcy5faGVpZ2h0LCAxLCAyMDAwKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhTC50YXJnZXQgPSBuZXcgVEhSRUUuVmVjdG9yMyggMCwgMCwgMCApO1xuICAgICAgICB0aGlzLl9jYW1lcmFSLnRhcmdldCA9IG5ldyBUSFJFRS5WZWN0b3IzKCAwLCAwLCAwICk7XG4gICAgfVxuXG4gICAgZGlzYWJsZVZSKCl7XG4gICAgICAgIHN1cGVyLmRpc2FibGVWUigpO1xuICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRWaWV3cG9ydCggMCwgMCwgdGhpcy5fd2lkdGgsIHRoaXMuX2hlaWdodCApO1xuICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRTY2lzc29yKCAwLCAwLCB0aGlzLl93aWR0aCwgdGhpcy5faGVpZ2h0ICk7XG4gICAgfVxuXG4gICAgaGFuZGxlUmVzaXplKCl7XG4gICAgICAgIHN1cGVyLmhhbmRsZVJlc2l6ZSgpO1xuICAgICAgICB0aGlzLl9jYW1lcmEuYXNwZWN0ID0gdGhpcy5fd2lkdGggLyB0aGlzLl9oZWlnaHQ7XG4gICAgICAgIHRoaXMuX2NhbWVyYS51cGRhdGVQcm9qZWN0aW9uTWF0cml4KCk7XG4gICAgICAgIGlmKHRoaXMuVlJNb2RlKXtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwuYXNwZWN0ID0gdGhpcy5fY2FtZXJhLmFzcGVjdCAvIDI7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFSLmFzcGVjdCA9IHRoaXMuX2NhbWVyYS5hc3BlY3QgLyAyO1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhTC51cGRhdGVQcm9qZWN0aW9uTWF0cml4KCk7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFSLnVwZGF0ZVByb2plY3Rpb25NYXRyaXgoKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGhhbmRsZU1vdXNlV2hlZWwoZXZlbnQ6IGFueSl7XG4gICAgICAgIHN1cGVyLmhhbmRsZU1vdXNlV2hlZWwoZXZlbnQpO1xuXG4gICAgICAgIC8vIFdlYktpdFxuICAgICAgICBpZiAoIGV2ZW50LndoZWVsRGVsdGFZICkge1xuICAgICAgICAgICAgdGhpcy5fY2FtZXJhLmZvdiAtPSBldmVudC53aGVlbERlbHRhWSAqIDAuMDU7XG4gICAgICAgICAgICAvLyBPcGVyYSAvIEV4cGxvcmVyIDlcbiAgICAgICAgfSBlbHNlIGlmICggZXZlbnQud2hlZWxEZWx0YSApIHtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYS5mb3YgLT0gZXZlbnQud2hlZWxEZWx0YSAqIDAuMDU7XG4gICAgICAgICAgICAvLyBGaXJlZm94XG4gICAgICAgIH0gZWxzZSBpZiAoIGV2ZW50LmRldGFpbCApIHtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYS5mb3YgKz0gZXZlbnQuZGV0YWlsICogMS4wO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuX2NhbWVyYS5mb3YgPSBNYXRoLm1pbih0aGlzLm9wdGlvbnMubWF4Rm92LCB0aGlzLl9jYW1lcmEuZm92KTtcbiAgICAgICAgdGhpcy5fY2FtZXJhLmZvdiA9IE1hdGgubWF4KHRoaXMub3B0aW9ucy5taW5Gb3YsIHRoaXMuX2NhbWVyYS5mb3YpO1xuICAgICAgICB0aGlzLl9jYW1lcmEudXBkYXRlUHJvamVjdGlvbk1hdHJpeCgpO1xuICAgICAgICBpZih0aGlzLlZSTW9kZSl7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFMLmZvdiA9IHRoaXMuX2NhbWVyYS5mb3Y7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFSLmZvdiA9IHRoaXMuX2NhbWVyYS5mb3Y7XG4gICAgICAgICAgICB0aGlzLl9jYW1lcmFMLnVwZGF0ZVByb2plY3Rpb25NYXRyaXgoKTtcbiAgICAgICAgICAgIHRoaXMuX2NhbWVyYVIudXBkYXRlUHJvamVjdGlvbk1hdHJpeCgpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgaGFuZGxlVG91Y2hNb3ZlKGV2ZW50OiBhbnkpIHtcbiAgICAgICAgc3VwZXIuaGFuZGxlVG91Y2hNb3ZlKGV2ZW50KTtcblxuICAgICAgICBpZih0aGlzLl9pc1VzZXJQaW5jaCl7XG4gICAgICAgICAgICBsZXQgY3VycmVudERpc3RhbmNlID0gZ2V0VG91Y2hlc0Rpc3RhbmNlKGV2ZW50LnRvdWNoZXMpO1xuICAgICAgICAgICAgZXZlbnQud2hlZWxEZWx0YVkgPSAgKGN1cnJlbnREaXN0YW5jZSAtIHRoaXMuX211bHRpVG91Y2hEaXN0YW5jZSkgKiAyO1xuICAgICAgICAgICAgdGhpcy5oYW5kbGVNb3VzZVdoZWVsKGV2ZW50KTtcbiAgICAgICAgICAgIHRoaXMuX211bHRpVG91Y2hEaXN0YW5jZSA9IGN1cnJlbnREaXN0YW5jZTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIHJlbmRlcigpe1xuICAgICAgICBzdXBlci5yZW5kZXIoKTtcblxuICAgICAgICB0aGlzLl9jYW1lcmEudGFyZ2V0LnggPSA1MDAgKiBNYXRoLnNpbiggdGhpcy5fcGhpICkgKiBNYXRoLmNvcyggdGhpcy5fdGhldGEgKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhLnRhcmdldC55ID0gNTAwICogTWF0aC5jb3MoIHRoaXMuX3BoaSApO1xuICAgICAgICB0aGlzLl9jYW1lcmEudGFyZ2V0LnogPSA1MDAgKiBNYXRoLnNpbiggdGhpcy5fcGhpICkgKiBNYXRoLnNpbiggdGhpcy5fdGhldGEgKTtcbiAgICAgICAgdGhpcy5fY2FtZXJhLmxvb2tBdCggdGhpcy5fY2FtZXJhLnRhcmdldCApO1xuXG4gICAgICAgIGlmKCF0aGlzLlZSTW9kZSl7XG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5yZW5kZXIoIHRoaXMuX3NjZW5lLCB0aGlzLl9jYW1lcmEgKTtcbiAgICAgICAgfVxuICAgICAgICBlbHNle1xuICAgICAgICAgICAgbGV0IHZpZXdQb3J0V2lkdGggPSB0aGlzLl93aWR0aCAvIDIsIHZpZXdQb3J0SGVpZ2h0ID0gdGhpcy5faGVpZ2h0O1xuICAgICAgICAgICAgaWYodHlwZW9mIHdpbmRvdy52ckhNRCAhPT0gJ3VuZGVmaW5lZCcpe1xuICAgICAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwucHJvamVjdGlvbk1hdHJpeCA9IGZvdlRvUHJvamVjdGlvbiggdGhpcy5fZXllRk9WTCwgdHJ1ZSwgdGhpcy5fY2FtZXJhLm5lYXIsIHRoaXMuX2NhbWVyYS5mYXIgKTtcbiAgICAgICAgICAgICAgICB0aGlzLl9jYW1lcmFSLnByb2plY3Rpb25NYXRyaXggPSBmb3ZUb1Byb2plY3Rpb24oIHRoaXMuX2V5ZUZPVlIsIHRydWUsIHRoaXMuX2NhbWVyYS5uZWFyLCB0aGlzLl9jYW1lcmEuZmFyICk7XG4gICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICBsZXQgbG9uTCA9IHRoaXMuX2xvbiArIHRoaXMub3B0aW9ucy5WUkdhcERlZ3JlZTtcbiAgICAgICAgICAgICAgICBsZXQgbG9uUiA9IHRoaXMuX2xvbiAtIHRoaXMub3B0aW9ucy5WUkdhcERlZ3JlZTtcblxuICAgICAgICAgICAgICAgIGxldCB0aGV0YUwgPSBUSFJFRS5NYXRoLmRlZ1RvUmFkKCBsb25MICk7XG4gICAgICAgICAgICAgICAgbGV0IHRoZXRhUiA9IFRIUkVFLk1hdGguZGVnVG9SYWQoIGxvblIgKTtcblxuXG4gICAgICAgICAgICAgICAgdGhpcy5fY2FtZXJhTC50YXJnZXQueCA9IDUwMCAqIE1hdGguc2luKCB0aGlzLl9waGkgKSAqIE1hdGguY29zKCB0aGV0YUwgKTtcbiAgICAgICAgICAgICAgICB0aGlzLl9jYW1lcmFMLnRhcmdldC55ID0gdGhpcy5fY2FtZXJhLnRhcmdldC55O1xuICAgICAgICAgICAgICAgIHRoaXMuX2NhbWVyYUwudGFyZ2V0LnogPSA1MDAgKiBNYXRoLnNpbiggdGhpcy5fcGhpICkgKiBNYXRoLnNpbiggdGhldGFMICk7XG4gICAgICAgICAgICAgICAgdGhpcy5fY2FtZXJhTC5sb29rQXQodGhpcy5fY2FtZXJhTC50YXJnZXQpO1xuXG4gICAgICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi50YXJnZXQueCA9IDUwMCAqIE1hdGguc2luKCB0aGlzLl9waGkgKSAqIE1hdGguY29zKCB0aGV0YVIgKTtcbiAgICAgICAgICAgICAgICB0aGlzLl9jYW1lcmFSLnRhcmdldC55ID0gdGhpcy5fY2FtZXJhLnRhcmdldC55O1xuICAgICAgICAgICAgICAgIHRoaXMuX2NhbWVyYVIudGFyZ2V0LnogPSA1MDAgKiBNYXRoLnNpbiggdGhpcy5fcGhpICkgKiBNYXRoLnNpbiggdGhldGFSICk7XG4gICAgICAgICAgICAgICAgdGhpcy5fY2FtZXJhUi5sb29rQXQodGhpcy5fY2FtZXJhUi50YXJnZXQpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgLy8gcmVuZGVyIGxlZnQgZXllXG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5zZXRWaWV3cG9ydCggMCwgMCwgdmlld1BvcnRXaWR0aCwgdmlld1BvcnRIZWlnaHQgKTtcbiAgICAgICAgICAgIHRoaXMuX3JlbmRlcmVyLnNldFNjaXNzb3IoIDAsIDAsIHZpZXdQb3J0V2lkdGgsIHZpZXdQb3J0SGVpZ2h0ICk7XG4gICAgICAgICAgICB0aGlzLl9yZW5kZXJlci5yZW5kZXIoIHRoaXMuX3NjZW5lLCB0aGlzLl9jYW1lcmFMICk7XG5cbiAgICAgICAgICAgIC8vIHJlbmRlciByaWdodCBleWVcbiAgICAgICAgICAgIHRoaXMuX3JlbmRlcmVyLnNldFZpZXdwb3J0KCB2aWV3UG9ydFdpZHRoLCAwLCB2aWV3UG9ydFdpZHRoLCB2aWV3UG9ydEhlaWdodCApO1xuICAgICAgICAgICAgdGhpcy5fcmVuZGVyZXIuc2V0U2Npc3Nvciggdmlld1BvcnRXaWR0aCwgMCwgdmlld1BvcnRXaWR0aCwgdmlld1BvcnRIZWlnaHQgKTtcbiAgICAgICAgICAgIHRoaXMuX3JlbmRlcmVyLnJlbmRlciggdGhpcy5fc2NlbmUsIHRoaXMuX2NhbWVyYVIgKTtcbiAgICAgICAgfVxuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgVHdvRFZpZGVvOyIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyLCBTZXR0aW5ncyB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBUaHJlZURWaWRlbyBmcm9tICcuL1RocmVlRFZpZGVvJztcbmltcG9ydCBUSFJFRSBmcm9tIFwidGhyZWVcIjtcblxuY2xhc3MgVlIxODAzRCBleHRlbmRzIFRocmVlRFZpZGVve1xuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBTZXR0aW5ncywgcmVuZGVyRWxlbWVudDogSFRNTEVsZW1lbnQpe1xuICAgICAgICBzdXBlcihwbGF5ZXIsIG9wdGlvbnMsIHJlbmRlckVsZW1lbnQpO1xuXG4gICAgICAgIGxldCBnZW9tZXRyeUwgPSBuZXcgVEhSRUUuU3BoZXJlQnVmZmVyR2VvbWV0cnkoNTAwLCA2MCwgNDAsIDAsIE1hdGguUEkpLnRvTm9uSW5kZXhlZCgpO1xuICAgICAgICBsZXQgZ2VvbWV0cnlSID0gbmV3IFRIUkVFLlNwaGVyZUJ1ZmZlckdlb21ldHJ5KDUwMCwgNjAsIDQwLCAwLCBNYXRoLlBJKS50b05vbkluZGV4ZWQoKTtcblxuICAgICAgICBsZXQgdXZzTCA9IGdlb21ldHJ5TC5hdHRyaWJ1dGVzLnV2LmFycmF5O1xuICAgICAgICBsZXQgbm9ybWFsc0wgPSBnZW9tZXRyeUwuYXR0cmlidXRlcy5ub3JtYWwuYXJyYXk7XG4gICAgICAgIGZvciAoIGxldCBpID0gMDsgaSA8IG5vcm1hbHNMLmxlbmd0aCAvIDM7IGkgKysgKSB7XG4gICAgICAgICAgICB1dnNMWyBpICogMiBdID0gdXZzTFsgaSAqIDIgXSAvIDI7XG4gICAgICAgIH1cblxuICAgICAgICBsZXQgdXZzUiA9IGdlb21ldHJ5Ui5hdHRyaWJ1dGVzLnV2LmFycmF5O1xuICAgICAgICBsZXQgbm9ybWFsc1IgPSBnZW9tZXRyeVIuYXR0cmlidXRlcy5ub3JtYWwuYXJyYXk7XG4gICAgICAgIGZvciAoIGxldCBpID0gMDsgaSA8IG5vcm1hbHNSLmxlbmd0aCAvIDM7IGkgKysgKSB7XG4gICAgICAgICAgICB1dnNSWyBpICogMiBdID0gdXZzUlsgaSAqIDIgXSAvIDIgKyAwLjU7XG4gICAgICAgIH1cblxuICAgICAgICBnZW9tZXRyeUwuc2NhbGUoIC0gMSwgMSwgMSApO1xuICAgICAgICBnZW9tZXRyeVIuc2NhbGUoIC0gMSwgMSwgMSApO1xuXG4gICAgICAgIHRoaXMuX21lc2hMID0gbmV3IFRIUkVFLk1lc2goZ2VvbWV0cnlMLFxuICAgICAgICAgICAgbmV3IFRIUkVFLk1lc2hCYXNpY01hdGVyaWFsKHsgbWFwOiB0aGlzLl90ZXh0dXJlfSlcbiAgICAgICAgKTtcblxuICAgICAgICB0aGlzLl9tZXNoUiA9IG5ldyBUSFJFRS5NZXNoKGdlb21ldHJ5UixcbiAgICAgICAgICAgIG5ldyBUSFJFRS5NZXNoQmFzaWNNYXRlcmlhbCh7IG1hcDogdGhpcy5fdGV4dHVyZX0pXG4gICAgICAgICk7XG4gICAgICAgIHRoaXMuX21lc2hSLnBvc2l0aW9uLnNldCgxMDAwLCAwLCAwKTtcblxuICAgICAgICB0aGlzLl9zY2VuZS5hZGQodGhpcy5fbWVzaEwpO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgVlIxODAzRDsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdHlwZSB7IFBsYXllciwgU2V0dGluZ3MgfSBmcm9tICcuLi90eXBlcyc7XG5pbXBvcnQgVGhyZWVEVmlkZW8gZnJvbSAnLi9UaHJlZURWaWRlbyc7XG5pbXBvcnQgVEhSRUUgZnJvbSBcInRocmVlXCI7XG5cbmNsYXNzIFZSMzYwM0QgZXh0ZW5kcyBUaHJlZURWaWRlb3tcbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXI6IFBsYXllciwgb3B0aW9uczogU2V0dGluZ3MsIHJlbmRlckVsZW1lbnQ6IEhUTUxFbGVtZW50KXtcbiAgICAgICAgc3VwZXIocGxheWVyLCBvcHRpb25zLCByZW5kZXJFbGVtZW50KTtcblxuICAgICAgICBsZXQgZ2VvbWV0cnlMID0gbmV3IFRIUkVFLlNwaGVyZUJ1ZmZlckdlb21ldHJ5KDUwMCwgNjAsIDQwKS50b05vbkluZGV4ZWQoKTtcbiAgICAgICAgbGV0IGdlb21ldHJ5UiA9IG5ldyBUSFJFRS5TcGhlcmVCdWZmZXJHZW9tZXRyeSg1MDAsIDYwLCA0MCkudG9Ob25JbmRleGVkKCk7XG5cbiAgICAgICAgbGV0IHV2c0wgPSBnZW9tZXRyeUwuYXR0cmlidXRlcy51di5hcnJheTtcbiAgICAgICAgbGV0IG5vcm1hbHNMID0gZ2VvbWV0cnlMLmF0dHJpYnV0ZXMubm9ybWFsLmFycmF5O1xuICAgICAgICBmb3IgKCBsZXQgaSA9IDA7IGkgPCBub3JtYWxzTC5sZW5ndGggLyAzOyBpICsrICkge1xuICAgICAgICAgICAgdXZzTFsgaSAqIDIgKyAxIF0gPSB1dnNMWyBpICogMiArIDEgXSAvIDI7XG4gICAgICAgIH1cblxuICAgICAgICBsZXQgdXZzUiA9IGdlb21ldHJ5Ui5hdHRyaWJ1dGVzLnV2LmFycmF5O1xuICAgICAgICBsZXQgbm9ybWFsc1IgPSBnZW9tZXRyeVIuYXR0cmlidXRlcy5ub3JtYWwuYXJyYXk7XG4gICAgICAgIGZvciAoIGxldCBpID0gMDsgaSA8IG5vcm1hbHNSLmxlbmd0aCAvIDM7IGkgKysgKSB7XG4gICAgICAgICAgICB1dnNSWyBpICogMiArIDEgXSA9IHV2c1JbIGkgKiAyICsgMSBdIC8gMiArIDAuNTtcbiAgICAgICAgfVxuXG4gICAgICAgIGdlb21ldHJ5TC5zY2FsZSggLSAxLCAxLCAxICk7XG4gICAgICAgIGdlb21ldHJ5Ui5zY2FsZSggLSAxLCAxLCAxICk7XG5cbiAgICAgICAgdGhpcy5fbWVzaEwgPSBuZXcgVEhSRUUuTWVzaChnZW9tZXRyeUwsXG4gICAgICAgICAgICBuZXcgVEhSRUUuTWVzaEJhc2ljTWF0ZXJpYWwoeyBtYXA6IHRoaXMuX3RleHR1cmV9KVxuICAgICAgICApO1xuXG4gICAgICAgIHRoaXMuX21lc2hSID0gbmV3IFRIUkVFLk1lc2goZ2VvbWV0cnlSLFxuICAgICAgICAgICAgbmV3IFRIUkVFLk1lc2hCYXNpY01hdGVyaWFsKHsgbWFwOiB0aGlzLl90ZXh0dXJlfSlcbiAgICAgICAgKTtcbiAgICAgICAgdGhpcy5fbWVzaFIucG9zaXRpb24uc2V0KDEwMDAsIDAsIDApO1xuXG4gICAgICAgIHRoaXMuX3NjZW5lLmFkZCh0aGlzLl9tZXNoTCk7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBWUjM2MDNEOyIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHsgUGxheWVyIH0gZnJvbSAnLi4vdHlwZXMnO1xuaW1wb3J0IEJ1dHRvbiBmcm9tICcuL0J1dHRvbic7XG5cbmNsYXNzIFZSQnV0dG9uIGV4dGVuZHMgQnV0dG9ue1xuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBhbnkgPSB7fSl7XG4gICAgICAgIHN1cGVyKHBsYXllciwgb3B0aW9ucyk7XG4gICAgfVxuXG4gICAgYnVpbGRDU1NDbGFzcygpIHtcbiAgICAgICAgcmV0dXJuIGB2anMtVlItY29udHJvbCAke3N1cGVyLmJ1aWxkQ1NTQ2xhc3MoKX1gO1xuICAgIH1cblxuICAgIGhhbmRsZUNsaWNrKGV2ZW50OiBFdmVudCl7XG4gICAgICAgIHN1cGVyLmhhbmRsZUNsaWNrKGV2ZW50KTtcbiAgICAgICAgdGhpcy50b2dnbGVDbGFzcyhcImVuYWJsZVwiKTtcblxuICAgICAgICBsZXQgdmlkZW9DYW52YXMgPSB0aGlzLnBsYXllci5nZXRDb21wb25lbnQoXCJWaWRlb0NhbnZhc1wiKTtcbiAgICAgICAgbGV0IFZSTW9kZSA9IHZpZGVvQ2FudmFzLlZSTW9kZTtcbiAgICAgICAgKCFWUk1vZGUpPyB2aWRlb0NhbnZhcy5lbmFibGVWUigpIDogdmlkZW9DYW52YXMuZGlzYWJsZVZSKCk7XG4gICAgICAgICghVlJNb2RlKT8gIHRoaXMucGxheWVyLnRyaWdnZXIoJ1ZSTW9kZU9uJyk6IHRoaXMucGxheWVyLnRyaWdnZXIoJ1ZSTW9kZU9mZicpO1xuICAgICAgICBpZighVlJNb2RlICYmIHRoaXMub3B0aW9ucy5WUkZ1bGxzY3JlZW4pe1xuICAgICAgICAgICAgdGhpcy5wbGF5ZXIuZW5hYmxlRnVsbHNjcmVlbigpO1xuICAgICAgICB9XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBWUkJ1dHRvbjsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgbWFrZVZpZGVvUGxheWFibGVJbmxpbmUgZnJvbSAnaXBob25lLWlubGluZS12aWRlbyc7XG5pbXBvcnQgdHlwZSB7U2V0dGluZ3MsIFBsYXllciwgVmlkZW9UeXBlcywgQ29vcmRpbmF0ZXMsIEFuaW1hdGlvblNldHRpbmdzfSBmcm9tICcuL3R5cGVzL2luZGV4JztcbmltcG9ydCB0eXBlIEJhc2VDYW52YXMgZnJvbSAnLi9Db21wb25lbnRzL0Jhc2VDYW52YXMnO1xuaW1wb3J0IEV2ZW50RW1pdHRlciBmcm9tICd3b2xmeTg3LWV2ZW50ZW1pdHRlcic7XG5pbXBvcnQgRXF1aXJlY3Rhbmd1bGFyIGZyb20gJy4vQ29tcG9uZW50cy9FcXVpcmVjdGFuZ3VsYXInO1xuaW1wb3J0IEZpc2hleWUgZnJvbSAnLi9Db21wb25lbnRzL0Zpc2hleWUnO1xuaW1wb3J0IER1YWxGaXNoZXllIGZyb20gJy4vQ29tcG9uZW50cy9EdWFsRmlzaGV5ZSc7XG5pbXBvcnQgVlIzNjAzRCBmcm9tICcuL0NvbXBvbmVudHMvVlIzNjAzRCc7XG5pbXBvcnQgVlIxODAzRCBmcm9tICcuL0NvbXBvbmVudHMvVlIxODAzRCc7XG5pbXBvcnQgTm90aWZpY2F0aW9uIGZyb20gJy4vQ29tcG9uZW50cy9Ob3RpZmljYXRpb24nO1xuaW1wb3J0IFRodW1ibmFpbCBmcm9tICcuL0NvbXBvbmVudHMvVGh1bWJuYWlsJztcbmltcG9ydCBWUkJ1dHRvbiBmcm9tICcuL0NvbXBvbmVudHMvVlJCdXR0b24nO1xuaW1wb3J0IE1hcmtlckNvbnRhaW5lciBmcm9tICcuL0NvbXBvbmVudHMvTWFya2VyQ29udGFpbmVyJztcbmltcG9ydCBBbmltYXRpb24gZnJvbSAnLi9Db21wb25lbnRzL0FuaW1hdGlvbic7XG5pbXBvcnQgeyBEZXRlY3Rvciwgd2ViR0xFcnJvck1lc3NhZ2UsIGNyb3NzRG9tYWluV2FybmluZywgdHJhbnNpdGlvbkV2ZW50LCBtZXJnZU9wdGlvbnMsIG1vYmlsZUFuZFRhYmxldGNoZWNrLCBpc0lvcywgaXNSZWFsSXBob25lLCB3YXJuaW5nIH0gZnJvbSAnLi91dGlscyc7XG5cbmNvbnN0IHJ1bk9uTW9iaWxlID0gbW9iaWxlQW5kVGFibGV0Y2hlY2soKTtcblxuY29uc3QgdmlkZW9UeXBlcyA9IFtcImVxdWlyZWN0YW5ndWxhclwiLCBcImZpc2hleWVcIiwgXCJkdWFsX2Zpc2hleWVcIiwgXCJWUjE4MDNEXCIsIFwiVlIzNjAzRFwiXTtcblxuZXhwb3J0IGNvbnN0IGRlZmF1bHRzOiBTZXR0aW5ncyA9IHtcbiAgICB2aWRlb1R5cGU6IFwiZXF1aXJlY3Rhbmd1bGFyXCIsXG4gICAgTW91c2VFbmFibGU6IHRydWUsXG4gICAgY2xpY2tBbmREcmFnOiBmYWxzZSxcbiAgICBtb3ZpbmdTcGVlZDoge1xuICAgICAgICB4OiAwLjAwMDUsXG4gICAgICAgIHk6IDAuMDAwNVxuICAgIH0sXG4gICAgY2xpY2tUb1RvZ2dsZTogdHJ1ZSxcbiAgICBzY3JvbGxhYmxlOiB0cnVlLFxuICAgIHJlc2l6YWJsZTogdHJ1ZSxcbiAgICB1c2VIZWxwZXJDYW52YXM6IFwiYXV0b1wiLFxuICAgIGluaXRGb3Y6IDc1LFxuICAgIG1heEZvdjogMTA1LFxuICAgIG1pbkZvdjogNTEsXG4gICAgLy9pbml0aWFsIHBvc2l0aW9uIGZvciB0aGUgdmlkZW9cbiAgICBpbml0TGF0OiAwLFxuICAgIGluaXRMb246IDE4MCxcbiAgICAvL0EgZmxvYXQgdmFsdWUgYmFjayB0byBjZW50ZXIgd2hlbiBtb3VzZSBvdXQgdGhlIGNhbnZhcy4gVGhlIGhpZ2hlciwgdGhlIGZhc3Rlci5cbiAgICByZXR1cm5MYXRTcGVlZDogMC41LFxuICAgIHJldHVybkxvblNwZWVkOiAyLFxuICAgIGJhY2tUb0luaXRMYXQ6IGZhbHNlLFxuICAgIGJhY2tUb0luaXRMb246IGZhbHNlLFxuXG4gICAgLy9saW1pdCB2aWV3YWJsZSB6b29tXG4gICAgbWluTGF0OiAtODUsXG4gICAgbWF4TGF0OiA4NSxcblxuICAgIG1pbkxvbjogMCxcbiAgICBtYXhMb246IDM2MCxcblxuICAgIGF1dG9Nb2JpbGVPcmllbnRhdGlvbjogdHJ1ZSxcbiAgICBtb2JpbGVWaWJyYXRpb25WYWx1ZTogaXNJb3MoKT8gMC4wMjIgOiAxLFxuXG4gICAgVlJFbmFibGU6IHJ1bk9uTW9iaWxlLFxuICAgIFZSR2FwRGVncmVlOiAwLjUsXG4gICAgVlJGdWxsc2NyZWVuOiB0cnVlLC8vYXV0byBmdWxsc2NyZWVuIHdoZW4gaW4gdnIgbW9kZVxuXG4gICAgUGFub3JhbWFUaHVtYm5haWw6IGZhbHNlLFxuICAgIEtleWJvYXJkQ29udHJvbDogZmFsc2UsXG4gICAgS2V5Ym9hcmRNb3ZpbmdTcGVlZDoge1xuICAgICAgICB4OiAxLFxuICAgICAgICB5OiAxXG4gICAgfSxcblxuICAgIFNwaGVyZTp7XG4gICAgICAgIHJvdGF0ZVg6IDAsXG4gICAgICAgIHJvdGF0ZVk6IDAsXG4gICAgICAgIHJvdGF0ZVo6IDBcbiAgICB9LFxuXG4gICAgZHVhbEZpc2g6IHtcbiAgICAgICAgd2lkdGg6IDE5MjAsXG4gICAgICAgIGhlaWdodDogMTA4MCxcbiAgICAgICAgY2lyY2xlMToge1xuICAgICAgICAgICAgeDogMC4yNDA2MjUsXG4gICAgICAgICAgICB5OiAwLjU1MzcwNCxcbiAgICAgICAgICAgIHJ4OiAwLjIzMzMzLFxuICAgICAgICAgICAgcnk6IDAuNDMxNDgsXG4gICAgICAgICAgICBjb3Zlclg6IDAuOTEzLFxuICAgICAgICAgICAgY292ZXJZOiAwLjlcbiAgICAgICAgfSxcbiAgICAgICAgY2lyY2xlMjoge1xuICAgICAgICAgICAgeDogMC43NTcyOTIsXG4gICAgICAgICAgICB5OiAwLjU1MzcwNCxcbiAgICAgICAgICAgIHJ4OiAwLjIzMjI5MixcbiAgICAgICAgICAgIHJ5OiAwLjQyOTYyOTYsXG4gICAgICAgICAgICBjb3Zlclg6IDAuOTEzLFxuICAgICAgICAgICAgY292ZXJZOiAwLjkzMDhcbiAgICAgICAgfVxuICAgIH0sXG5cbiAgICBOb3RpY2U6IHtcbiAgICAgICAgRW5hYmxlOiB0cnVlLFxuICAgICAgICBNZXNzYWdlOiBcIlBsZWFzZSB1c2UgeW91ciBtb3VzZSBkcmFnIGFuZCBkcm9wIHRoZSB2aWRlby5cIixcbiAgICAgICAgSGlkZVRpbWU6IDMwMDAsXG4gICAgfSxcblxuICAgIE1hcmtlcnM6IGZhbHNlLFxuXG4gICAgQW5pbWF0aW9uczogZmFsc2Vcbn07XG5cbmV4cG9ydCBjb25zdCBWUjE4MERlZmF1bHRzOiBhbnkgPSB7XG4gICAgLy9pbml0aWFsIHBvc2l0aW9uIGZvciB0aGUgdmlkZW9cbiAgICBpbml0TGF0OiAwLFxuICAgIGluaXRMb246IDkwLFxuICAgIC8vbGltaXQgdmlld2FibGUgem9vbVxuICAgIG1pbkxhdDogLTc1LFxuICAgIG1heExhdDogNTUsXG5cbiAgICBtaW5Mb246IDUwLFxuICAgIG1heExvbjogMTMwLFxuXG4gICAgY2xpY2tBbmREcmFnOiB0cnVlXG59O1xuXG4vKipcbiAqIHBhbm9yYW1hIGNvbnRyb2xsZXIgY2xhc3Mgd2hpY2ggY29udHJvbCByZXF1aXJlZCBjb21wb25lbnRzXG4gKi9cbmNsYXNzIFBhbm9yYW1hIGV4dGVuZHMgRXZlbnRFbWl0dGVye1xuICAgIF9vcHRpb25zOiBTZXR0aW5ncztcbiAgICBfcGxheWVyOiBQbGF5ZXI7XG4gICAgX3ZpZGVvQ2FudmFzOiBCYXNlQ2FudmFzO1xuICAgIF90aHVtYm5haWxDYW52YXM6IEJhc2VDYW52YXMgfCBudWxsO1xuICAgIF9hbmltYXRpb246IEFuaW1hdGlvbjtcblxuICAgIC8qKlxuICAgICAqIGNoZWNrIGxlZ2FjeSBvcHRpb24gc2V0dGluZ3MgYW5kIHByb2R1Y2Ugd2FybmluZyBtZXNzYWdlIGlmIHVzZXIgdXNlIGxlZ2FjeSBvcHRpb25zLCBhdXRvbWF0aWNhbGx5IHNldCBpdCB0byBuZXcgb3B0aW9ucy5cbiAgICAgKiBAcGFyYW0gb3B0aW9ucyB0aGUgb3B0aW9uIHNldHRpbmdzIHdoaWNoIHVzZXIgcGFyc2UuXG4gICAgICogQHJldHVybnMgeyp9IHRoZSBsYXRlc3QgdmVyc2lvbiB3aGljaCB3ZSB1c2UuXG4gICAgICovXG4gICAgc3RhdGljIGNoZWNrT3B0aW9ucyhvcHRpb25zOiBTZXR0aW5ncyk6IHZvaWQge1xuICAgICAgICBpZihvcHRpb25zLnZpZGVvVHlwZSA9PT0gXCIzZFZpZGVvXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgdmlkZW9UeXBlOiAke1N0cmluZyhvcHRpb25zLnZpZGVvVHlwZSl9IGlzIGRlcHJlY2F0ZWQsIHBsZWFzZSB1c2UgVlIzNjAzRGApO1xuICAgICAgICAgICAgb3B0aW9ucy52aWRlb1R5cGUgPSBcIlZSMzYwM0RcIjtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIGlmKG9wdGlvbnMudmlkZW9UeXBlICYmIHZpZGVvVHlwZXMuaW5kZXhPZihvcHRpb25zLnZpZGVvVHlwZSkgPT09IC0xKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYHZpZGVvVHlwZTogJHtTdHJpbmcob3B0aW9ucy52aWRlb1R5cGUpfSBpcyBub3Qgc3VwcG9ydGVkLCBzZXQgdmlkZW8gdHlwZSB0byAke1N0cmluZyhkZWZhdWx0cy52aWRlb1R5cGUpfS5gKTtcbiAgICAgICAgICAgIG9wdGlvbnMudmlkZW9UeXBlID0gZGVmYXVsdHMudmlkZW9UeXBlO1xuICAgICAgICB9XG5cbiAgICAgICAgaWYodHlwZW9mIG9wdGlvbnMuYmFja1RvVmVydGljYWxDZW50ZXIgIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgYmFja1RvVmVydGljYWxDZW50ZXIgaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSBiYWNrVG9Jbml0TGF0LmApO1xuICAgICAgICAgICAgb3B0aW9ucy5iYWNrVG9Jbml0TGF0ID0gb3B0aW9ucy5iYWNrVG9WZXJ0aWNhbENlbnRlcjtcbiAgICAgICAgfVxuICAgICAgICBpZih0eXBlb2Ygb3B0aW9ucy5iYWNrVG9Ib3Jpem9uQ2VudGVyICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYGJhY2tUb0hvcml6b25DZW50ZXIgaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSBiYWNrVG9Jbml0TG9uLmApO1xuICAgICAgICAgICAgb3B0aW9ucy5iYWNrVG9Jbml0TG9uID0gb3B0aW9ucy5iYWNrVG9Ib3Jpem9uQ2VudGVyO1xuICAgICAgICB9XG4gICAgICAgIGlmKHR5cGVvZiBvcHRpb25zLnJldHVyblN0ZXBMYXQgIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgcmV0dXJuU3RlcExhdCBpcyBkZXByZWNhdGVkLCBwbGVhc2UgdXNlIHJldHVybkxhdFNwZWVkLmApO1xuICAgICAgICAgICAgb3B0aW9ucy5yZXR1cm5MYXRTcGVlZCA9IG9wdGlvbnMucmV0dXJuU3RlcExhdDtcbiAgICAgICAgfVxuICAgICAgICBpZih0eXBlb2Ygb3B0aW9ucy5yZXR1cm5TdGVwTG9uICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYHJldHVyblN0ZXBMb24gaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSByZXR1cm5Mb25TcGVlZC5gKTtcbiAgICAgICAgICAgIG9wdGlvbnMucmV0dXJuTG9uU3BlZWQgPSBvcHRpb25zLnJldHVyblN0ZXBMb247XG4gICAgICAgIH1cbiAgICAgICAgaWYodHlwZW9mIG9wdGlvbnMuaGVscGVyQ2FudmFzICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYGhlbHBlckNhbnZhcyBpcyBkZXByZWNhdGVkLCB5b3UgZG9uJ3QgaGF2ZSB0byBzZXQgaXQgdXAgb24gbmV3IHZlcnNpb24uYCk7XG4gICAgICAgIH1cbiAgICAgICAgaWYodHlwZW9mIG9wdGlvbnMuY2FsbGJhY2sgIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgY2FsbGJhY2sgaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSByZWFkeS5gKTtcbiAgICAgICAgICAgIG9wdGlvbnMucmVhZHkgPSBvcHRpb25zLmNhbGxiYWNrO1xuICAgICAgICB9XG4gICAgICAgIGlmKHR5cGVvZiBvcHRpb25zLlNwaGVyZSA9PT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgICAgICBvcHRpb25zLlNwaGVyZSA9IHt9O1xuICAgICAgICB9XG4gICAgICAgIGlmKHR5cGVvZiBvcHRpb25zLnJvdGF0ZVggIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgcm90YXRlWCBpcyBkZXByZWNhdGVkLCBwbGVhc2UgdXNlIFNwaGVyZTp7IHJvdGF0ZVg6IDAsIHJvdGF0ZVk6IDAsIHJvdGF0ZVo6IDB9LmApO1xuICAgICAgICAgICAgaWYob3B0aW9ucy5TcGhlcmUpe1xuICAgICAgICAgICAgICAgIG9wdGlvbnMuU3BoZXJlLnJvdGF0ZVggPSBvcHRpb25zLnJvdGF0ZVg7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgaWYodHlwZW9mIG9wdGlvbnMucm90YXRlWSAhPT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgICAgICB3YXJuaW5nKGByb3RhdGVZIGlzIGRlcHJlY2F0ZWQsIHBsZWFzZSB1c2UgU3BoZXJlOnsgcm90YXRlWDogMCwgcm90YXRlWTogMCwgcm90YXRlWjogMH0uYCk7XG4gICAgICAgICAgICBpZihvcHRpb25zLlNwaGVyZSl7XG4gICAgICAgICAgICAgICAgb3B0aW9ucy5TcGhlcmUucm90YXRlWSA9IG9wdGlvbnMucm90YXRlWTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBpZih0eXBlb2Ygb3B0aW9ucy5yb3RhdGVaICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYHJvdGF0ZVogaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSBTcGhlcmU6eyByb3RhdGVYOiAwLCByb3RhdGVZOiAwLCByb3RhdGVaOiAwfS5gKTtcbiAgICAgICAgICAgIGlmKG9wdGlvbnMuU3BoZXJlKXtcbiAgICAgICAgICAgICAgICBvcHRpb25zLlNwaGVyZS5yb3RhdGVZID0gb3B0aW9ucy5yb3RhdGVaO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIGlmKHR5cGVvZiBvcHRpb25zLk5vdGljZSA9PT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgICAgICBvcHRpb25zLk5vdGljZSA9IHt9O1xuICAgICAgICB9XG4gICAgICAgIGlmKHR5cGVvZiBvcHRpb25zLnNob3dOb3RpY2UgIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICAgICAgd2FybmluZyhgc2hvd05vdGljZSBpcyBkZXByZWNhdGVkLCBwbGVhc2UgdXNlIE5vdGljZTogeyBFbmFibGU6IHRydWUgfWApO1xuICAgICAgICAgICAgaWYob3B0aW9ucy5Ob3RpY2Upe1xuICAgICAgICAgICAgICAgIG9wdGlvbnMuTm90aWNlLkVuYWJsZSA9IG9wdGlvbnMuc2hvd05vdGljZTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBpZih0eXBlb2Ygb3B0aW9ucy5Ob3RpY2VNZXNzYWdlICE9PSBcInVuZGVmaW5lZFwiKXtcbiAgICAgICAgICAgIHdhcm5pbmcoYE5vdGljZU1lc3NhZ2UgaXMgZGVwcmVjYXRlZCwgcGxlYXNlIHVzZSBOb3RpY2U6IHsgTWVzc2FnZTogXCJcIiB9YCk7XG4gICAgICAgICAgICBpZihvcHRpb25zLk5vdGljZSl7XG4gICAgICAgICAgICAgICAgb3B0aW9ucy5Ob3RpY2UuTWVzc2FnZSA9IG9wdGlvbnMuTm90aWNlTWVzc2FnZTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBpZih0eXBlb2Ygb3B0aW9ucy5hdXRvSGlkZU5vdGljZSAhPT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgICAgICB3YXJuaW5nKGBhdXRvSGlkZU5vdGljZSBpcyBkZXByZWNhdGVkLCBwbGVhc2UgdXNlIE5vdGljZTogeyBIaWRlVGltZTogMzAwMCB9YCk7XG4gICAgICAgICAgICBpZihvcHRpb25zLk5vdGljZSl7XG4gICAgICAgICAgICAgICAgb3B0aW9ucy5Ob3RpY2UuSGlkZVRpbWUgPSBvcHRpb25zLmF1dG9IaWRlTm90aWNlO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxuXG4gICAgc3RhdGljIGNob29zZVZpZGVvQ29tcG9uZW50KHZpZGVvVHlwZTogVmlkZW9UeXBlcyk6IENsYXNzPEJhc2VDYW52YXM+e1xuICAgICAgICBsZXQgVmlkZW9DbGFzczogQ2xhc3M8QmFzZUNhbnZhcz47XG4gICAgICAgIHN3aXRjaCh2aWRlb1R5cGUpe1xuICAgICAgICAgICAgY2FzZSBcImVxdWlyZWN0YW5ndWxhclwiOlxuICAgICAgICAgICAgICAgIFZpZGVvQ2xhc3MgPSBFcXVpcmVjdGFuZ3VsYXI7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICBjYXNlIFwiZmlzaGV5ZVwiOlxuICAgICAgICAgICAgICAgIFZpZGVvQ2xhc3MgPSBGaXNoZXllO1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgY2FzZSBcImR1YWxfZmlzaGV5ZVwiOlxuICAgICAgICAgICAgICAgIFZpZGVvQ2xhc3MgPSBEdWFsRmlzaGV5ZTtcbiAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgIGNhc2UgXCJWUjM2MDNEXCI6XG4gICAgICAgICAgICAgICAgVmlkZW9DbGFzcyA9IFZSMzYwM0Q7XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICBjYXNlIFwiVlIxODAzRFwiOlxuICAgICAgICAgICAgICAgIFZpZGVvQ2xhc3MgPSBWUjE4MDNEO1xuICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICAgICAgICBWaWRlb0NsYXNzID0gRXF1aXJlY3Rhbmd1bGFyO1xuICAgICAgICB9XG4gICAgICAgIHJldHVybiBWaWRlb0NsYXNzO1xuICAgIH1cblxuICAgIGNvbnN0cnVjdG9yKHBsYXllcjogUGxheWVyLCBvcHRpb25zOiBhbnkgPSB7fSl7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIFBhbm9yYW1hLmNoZWNrT3B0aW9ucyhvcHRpb25zKTtcbiAgICAgICAgaWYob3B0aW9ucy52aWRlb1R5cGUgPT09IFwiVlIxODAzRFwiKXtcbiAgICAgICAgICAgIG9wdGlvbnMgPSBtZXJnZU9wdGlvbnMoe30sIFZSMTgwRGVmYXVsdHMsIG9wdGlvbnMpO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuX29wdGlvbnMgPSBtZXJnZU9wdGlvbnMoe30sIGRlZmF1bHRzLCBvcHRpb25zKTtcbiAgICAgICAgdGhpcy5fcGxheWVyID0gcGxheWVyO1xuXG4gICAgICAgIHRoaXMucGxheWVyLmFkZENsYXNzKFwidmpzLXBhbm9yYW1hXCIpO1xuXG4gICAgICAgIGlmKCFEZXRlY3Rvci53ZWJnbCl7XG4gICAgICAgICAgICB0aGlzLnBvcHVwTm90aWZpY2F0aW9uKHdlYkdMRXJyb3JNZXNzYWdlKCkpO1xuICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICB9XG5cbiAgICAgICAgbGV0IFZpZGVvQ2xhc3MgPSBQYW5vcmFtYS5jaG9vc2VWaWRlb0NvbXBvbmVudCh0aGlzLm9wdGlvbnMudmlkZW9UeXBlKTtcbiAgICAgICAgLy9yZW5kZXIgMzYwIHRodW1ibmFpbFxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuUGFub3JhbWFUaHVtYm5haWwgJiYgcGxheWVyLmdldFRodW1ibmFpbFVSTCgpKXtcbiAgICAgICAgICAgIGxldCB0aHVtYm5haWxVUkwgPSBwbGF5ZXIuZ2V0VGh1bWJuYWlsVVJMKCk7XG4gICAgICAgICAgICBsZXQgcG9zdGVyID0gbmV3IFRodW1ibmFpbChwbGF5ZXIsIHtcbiAgICAgICAgICAgICAgICBwb3N0ZXJTcmM6IHRodW1ibmFpbFVSTCxcbiAgICAgICAgICAgICAgICBvbkNvbXBsZXRlOiAoKT0+e1xuICAgICAgICAgICAgICAgICAgICBpZih0aGlzLnRodW1ibmFpbENhbnZhcyl7XG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnRodW1ibmFpbENhbnZhcy5fdGV4dHVyZS5uZWVkc1VwZGF0ZSA9IHRydWU7XG4gICAgICAgICAgICAgICAgICAgICAgICB0aGlzLnRodW1ibmFpbENhbnZhcy5zdGFydEFuaW1hdGlvbigpO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB0aGlzLnBsYXllci5hZGRDb21wb25lbnQoXCJUaHVtYm5haWxcIiwgcG9zdGVyKTtcblxuICAgICAgICAgICAgcG9zdGVyLmVsKCkuc3R5bGUuZGlzcGxheSA9IFwibm9uZVwiO1xuICAgICAgICAgICAgdGhpcy5fdGh1bWJuYWlsQ2FudmFzID0gbmV3IFZpZGVvQ2xhc3MocGxheWVyLCB0aGlzLm9wdGlvbnMsIHBvc3Rlci5lbCgpKTtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLmFkZENvbXBvbmVudChcIlRodW1ibmFpbENhbnZhc1wiLCB0aGlzLnRodW1ibmFpbENhbnZhcyk7XG5cbiAgICAgICAgICAgIHRoaXMucGxheWVyLm9uZShcInBsYXlcIiwgKCkgPT4ge1xuICAgICAgICAgICAgICAgIHRoaXMudGh1bWJuYWlsQ2FudmFzICYmIHRoaXMudGh1bWJuYWlsQ2FudmFzLmhpZGUoKTtcbiAgICAgICAgICAgICAgICB0aGlzLnBsYXllci5yZW1vdmVDb21wb25lbnQoXCJUaHVtYm5haWxcIik7XG4gICAgICAgICAgICAgICAgdGhpcy5wbGF5ZXIucmVtb3ZlQ29tcG9uZW50KFwiVGh1bWJuYWlsQ2FudmFzXCIpO1xuICAgICAgICAgICAgICAgIHRoaXMuX3RodW1ibmFpbENhbnZhcyA9IG51bGw7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgfVxuXG4gICAgICAgIC8vZW5hYmxlIGlubGluZSBwbGF5IG9uIG1vYmlsZVxuICAgICAgICBpZihydW5Pbk1vYmlsZSl7XG4gICAgICAgICAgICBsZXQgdmlkZW9FbGVtZW50ID0gdGhpcy5wbGF5ZXIuZ2V0VmlkZW9FbCgpO1xuICAgICAgICAgICAgaWYoaXNSZWFsSXBob25lKCkpe1xuICAgICAgICAgICAgICAgIC8vaW9zIDEwIHN1cHBvcnQgcGxheSB2aWRlbyBpbmxpbmVcbiAgICAgICAgICAgICAgICB2aWRlb0VsZW1lbnQuc2V0QXR0cmlidXRlKFwicGxheXNpbmxpbmVcIiwgXCJcIik7XG4gICAgICAgICAgICAgICAgbWFrZVZpZGVvUGxheWFibGVJbmxpbmUodmlkZW9FbGVtZW50LCB0cnVlKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHRoaXMucGxheWVyLmFkZENsYXNzKFwidmpzLXBhbm9yYW1hLW1vYmlsZS1pbmxpbmUtdmlkZW9cIik7XG4gICAgICAgICAgICAvL2J5IGRlZmF1bHQgdmlkZW9qcyBoaWRlIGNvbnRyb2wgYmFyIG9uIG1vYmlsZSBkZXZpY2UuXG4gICAgICAgICAgICB0aGlzLnBsYXllci5yZW1vdmVDbGFzcyhcInZqcy11c2luZy1uYXRpdmUtY29udHJvbHNcIik7XG4gICAgICAgIH1cblxuICAgICAgICAvL2FkZCB2ciBpY29uIHRvIHBsYXllclxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuVlJFbmFibGUpe1xuICAgICAgICAgICAgbGV0IGNvbnRyb2xiYXIgPSB0aGlzLnBsYXllci5jb250cm9sQmFyKCk7XG4gICAgICAgICAgICBsZXQgaW5kZXggPSBjb250cm9sYmFyLmNoaWxkTm9kZXMubGVuZ3RoO1xuICAgICAgICAgICAgbGV0IHZyQnV0dG9uID0gbmV3IFZSQnV0dG9uKHBsYXllciwgdGhpcy5vcHRpb25zKTtcbiAgICAgICAgICAgIHZyQnV0dG9uLmRpc2FibGUoKTtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLmFkZENvbXBvbmVudChcIlZSQnV0dG9uXCIsIHZyQnV0dG9uLCB0aGlzLnBsYXllci5jb250cm9sQmFyKCksIGluZGV4IC0gMSk7XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLnBsYXllci5yZWFkeSgoKT0+e1xuICAgICAgICAgICAgLy9hZGQgY2FudmFzIHRvIHBsYXllclxuICAgICAgICAgICAgdGhpcy5fdmlkZW9DYW52YXMgPSBuZXcgVmlkZW9DbGFzcyhwbGF5ZXIsIHRoaXMub3B0aW9ucywgcGxheWVyLmdldFZpZGVvRWwoKSk7XG4gICAgICAgICAgICB0aGlzLnZpZGVvQ2FudmFzLmhpZGUoKTtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLmFkZENvbXBvbmVudChcIlZpZGVvQ2FudmFzXCIsIHRoaXMudmlkZW9DYW52YXMpO1xuXG4gICAgICAgICAgICB0aGlzLmF0dGFjaEV2ZW50cygpO1xuXG4gICAgICAgICAgICBpZih0aGlzLm9wdGlvbnMuVlJFbmFibGUpe1xuICAgICAgICAgICAgICAgIGxldCB2ckJ1dHRvbiA9IHRoaXMucGxheWVyLmdldENvbXBvbmVudChcIlZSQnV0dG9uXCIpO1xuICAgICAgICAgICAgICAgIHZyQnV0dG9uICYmIHZyQnV0dG9uLmVuYWJsZSgpO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICBpZih0aGlzLm9wdGlvbnMucmVhZHkpe1xuICAgICAgICAgICAgICAgIHRoaXMub3B0aW9ucy5yZWFkeS5jYWxsKHRoaXMpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICAvL3JlZ2lzdGVyIHRyaWdnZXIgY2FsbGJhY2sgZnVuY3Rpb24sIHNvIGV2ZXJ5dGhpbmcgdHJpZ2dlciB0byBwbGF5ZXIgd2lsbCBhbHNvIHRyaWdnZXIgaW4gaGVyZVxuICAgICAgICB0aGlzLnBsYXllci5yZWdpc3RlclRyaWdnZXJDYWxsYmFjaygoZXZlbnROYW1lKT0+e1xuICAgICAgICAgICAgdGhpcy50cmlnZ2VyKGV2ZW50TmFtZSk7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIGRpc3Bvc2UoKXtcbiAgICAgICAgdGhpcy5kZXRhY2hFdmVudHMoKTtcbiAgICAgICAgdGhpcy5wbGF5ZXIuZ2V0VmlkZW9FbCgpLnN0eWxlLnZpc2liaWxpdHkgPSBcInZpc2libGVcIjtcbiAgICAgICAgdGhpcy5wbGF5ZXIucmVtb3ZlQ29tcG9uZW50KFwiVmlkZW9DYW52YXNcIik7XG4gICAgfVxuXG4gICAgYXR0YWNoRXZlbnRzKCl7XG4gICAgICAgIC8vc2hvdyBub3RpY2UgbWVzc2FnZVxuICAgICAgICBpZih0aGlzLm9wdGlvbnMuTm90aWNlICYmIHRoaXMub3B0aW9ucy5Ob3RpY2UuRW5hYmxlKXtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLm9uZShcInBsYXlpbmdcIiwgKCk9PntcbiAgICAgICAgICAgICAgICBsZXQgbWVzc2FnZSA9IHRoaXMub3B0aW9ucy5Ob3RpY2UgJiYgdGhpcy5vcHRpb25zLk5vdGljZS5NZXNzYWdlIHx8IFwiXCI7XG4gICAgICAgICAgICAgICAgdGhpcy5wb3B1cE5vdGlmaWNhdGlvbihtZXNzYWdlKTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICB9XG5cbiAgICAgICAgLy9lbmFibGUgY2FudmFzIHJlbmRlcmluZyB3aGVuIHZpZGVvIGlzIHBsYXlpbmdcbiAgICAgICAgY29uc3QgaGFuZGxlUGxheSA9ICgpID0+IHtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLmdldFZpZGVvRWwoKS5zdHlsZS52aXNpYmlsaXR5ID0gXCJoaWRkZW5cIjtcbiAgICAgICAgICAgIHRoaXMudmlkZW9DYW52YXMuc3RhcnRBbmltYXRpb24oKTtcbiAgICAgICAgICAgIHRoaXMudmlkZW9DYW52YXMuc2hvdygpO1xuXG4gICAgICAgICAgICAvL2luaXRpYWwgbWFya2Vyc1xuICAgICAgICAgICAgaWYodGhpcy5vcHRpb25zLk1hcmtlcnMgJiYgQXJyYXkuaXNBcnJheSh0aGlzLm9wdGlvbnMuTWFya2Vycykpe1xuICAgICAgICAgICAgICAgIGxldCBtYXJrZXJDb250YWluZXIgPSBuZXcgTWFya2VyQ29udGFpbmVyKHRoaXMucGxheWVyLCB7XG4gICAgICAgICAgICAgICAgICAgIGNhbnZhczogdGhpcy52aWRlb0NhbnZhcyxcbiAgICAgICAgICAgICAgICAgICAgbWFya2VyczogdGhpcy5vcHRpb25zLk1hcmtlcnMsXG4gICAgICAgICAgICAgICAgICAgIFZSRW5hYmxlOiB0aGlzLm9wdGlvbnMuVlJFbmFibGVcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgICAgICB0aGlzLnBsYXllci5hZGRDb21wb25lbnQoXCJtYXJrZXJDb250YWluZXJcIiwgbWFya2VyQ29udGFpbmVyKTtcbiAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgLy9pbml0aWFsIGFuaW1hdGlvbnNcbiAgICAgICAgICAgIGlmKHRoaXMub3B0aW9ucy5BbmltYXRpb24gJiYgQXJyYXkuaXNBcnJheSh0aGlzLm9wdGlvbnMuQW5pbWF0aW9uKSl7XG4gICAgICAgICAgICAgICAgdGhpcy5fYW5pbWF0aW9uID0gbmV3IEFuaW1hdGlvbih0aGlzLnBsYXllciwge1xuICAgICAgICAgICAgICAgICAgICBhbmltYXRpb246IHRoaXMub3B0aW9ucy5BbmltYXRpb24sXG4gICAgICAgICAgICAgICAgICAgIGNhbnZhczogdGhpcy52aWRlb0NhbnZhc1xuICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICAvL2RldGVjdCBibGFjayBzY3JlZW5cbiAgICAgICAgICAgIGlmKHdpbmRvdy5jb25zb2xlICYmIHdpbmRvdy5jb25zb2xlLmVycm9yKXtcbiAgICAgICAgICAgICAgICBsZXQgb3JpZ2luYWxFcnJvckZ1bmN0aW9uID0gd2luZG93LmNvbnNvbGUuZXJyb3I7XG4gICAgICAgICAgICAgICAgbGV0IG9yaWdpbmFsV2FybkZ1bmN0aW9uID0gd2luZG93LmNvbnNvbGUud2FybjtcbiAgICAgICAgICAgICAgICB3aW5kb3cuY29uc29sZS5lcnJvciA9IChlcnJvcik9PntcbiAgICAgICAgICAgICAgICAgICAgaWYoZXJyb3IubWVzc2FnZS5pbmRleE9mKFwiaW5zZWN1cmVcIikgIT09IC0xKXtcbiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXMucG9wdXBOb3RpZmljYXRpb24oY3Jvc3NEb21haW5XYXJuaW5nKCkpO1xuICAgICAgICAgICAgICAgICAgICAgICAgdGhpcy5kaXNwb3NlKCk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9O1xuICAgICAgICAgICAgICAgIHdpbmRvdy5jb25zb2xlLndhcm4gPSAod2FybikgPT57XG4gICAgICAgICAgICAgICAgICAgIGlmKHdhcm4uaW5kZXhPZihcImdsLmdldFNoYWRlckluZm9Mb2dcIikgIT09IC0xKXtcbiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXMucG9wdXBOb3RpZmljYXRpb24oY3Jvc3NEb21haW5XYXJuaW5nKCkpO1xuICAgICAgICAgICAgICAgICAgICAgICAgdGhpcy5kaXNwb3NlKCk7XG4gICAgICAgICAgICAgICAgICAgICAgICB3aW5kb3cuY29uc29sZS53YXJuID0gb3JpZ2luYWxXYXJuRnVuY3Rpb247XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9O1xuICAgICAgICAgICAgICAgIHNldFRpbWVvdXQoKCk9PntcbiAgICAgICAgICAgICAgICAgICAgd2luZG93LmNvbnNvbGUuZXJyb3IgPSBvcmlnaW5hbEVycm9yRnVuY3Rpb247XG4gICAgICAgICAgICAgICAgICAgIHdpbmRvdy5jb25zb2xlLndhcm4gPSBvcmlnaW5hbFdhcm5GdW5jdGlvbjtcbiAgICAgICAgICAgICAgICB9LCA1MDApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9O1xuICAgICAgICBpZighdGhpcy5wbGF5ZXIucGF1c2VkKCkpe1xuICAgICAgICAgICAgaGFuZGxlUGxheSgpO1xuICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgIHRoaXMucGxheWVyLm9uZShcInBsYXlcIiwgaGFuZGxlUGxheSk7XG4gICAgICAgIH1cblxuICAgICAgICBjb25zdCByZXBvcnQgPSAoKSA9PiB7XG4gICAgICAgICAgICB0aGlzLnBsYXllci5yZXBvcnRVc2VyQWN0aXZpdHkoKTtcbiAgICAgICAgfTtcblxuICAgICAgICB0aGlzLnZpZGVvQ2FudmFzLmFkZExpc3RlbmVycyh7XG4gICAgICAgICAgICBcInRvdWNoTW92ZVwiOiByZXBvcnQsXG4gICAgICAgICAgICBcInRhcFwiOiByZXBvcnRcbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgZGV0YWNoRXZlbnRzKCl7XG4gICAgICAgIGlmKHRoaXMudGh1bWJuYWlsQ2FudmFzKXtcbiAgICAgICAgICAgIHRoaXMudGh1bWJuYWlsQ2FudmFzLnN0b3BBbmltYXRpb24oKTtcbiAgICAgICAgfVxuICAgICAgICBpZih0aGlzLnZpZGVvQ2FudmFzKXtcbiAgICAgICAgICAgIHRoaXMudmlkZW9DYW52YXMuc3RvcEFuaW1hdGlvbigpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgcG9wdXBOb3RpZmljYXRpb24obWVzc2FnZTogc3RyaW5nIHwgSFRNTEVsZW1lbnQpe1xuICAgICAgICBsZXQgbm90aWNlID0gdGhpcy5wbGF5ZXIuYWRkQ29tcG9uZW50KFwiTm90aWNlXCIsIG5ldyBOb3RpZmljYXRpb24odGhpcy5wbGF5ZXIsIHtcbiAgICAgICAgICAgIE1lc3NhZ2U6IG1lc3NhZ2VcbiAgICAgICAgfSkpO1xuXG4gICAgICAgIGlmKHRoaXMub3B0aW9ucy5Ob3RpY2UgJiYgdGhpcy5vcHRpb25zLk5vdGljZS5IaWRlVGltZSAmJiB0aGlzLm9wdGlvbnMuTm90aWNlLkhpZGVUaW1lID4gMCl7XG4gICAgICAgICAgICBzZXRUaW1lb3V0KGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgICAgICBub3RpY2UucmVtb3ZlQ2xhc3MoXCJ2anMtdmlkZW8tbm90aWNlLXNob3dcIik7XG4gICAgICAgICAgICAgICAgbm90aWNlLmFkZENsYXNzKFwidmpzLXZpZGVvLW5vdGljZS1mYWRlT3V0XCIpO1xuICAgICAgICAgICAgICAgIG5vdGljZS5vbmUodHJhbnNpdGlvbkV2ZW50LCAoKT0+e1xuICAgICAgICAgICAgICAgICAgICBub3RpY2UuaGlkZSgpO1xuICAgICAgICAgICAgICAgICAgICBub3RpY2UucmVtb3ZlQ2xhc3MoXCJ2anMtdmlkZW8tbm90aWNlLWZhZGVPdXRcIik7XG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICB9LCB0aGlzLm9wdGlvbnMuTm90aWNlLkhpZGVUaW1lKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGFkZFRpbWVsaW5lKGFuaW1hdGlvbjogQW5pbWF0aW9uU2V0dGluZ3MpIDogdm9pZHtcbiAgICAgICAgdGhpcy5fYW5pbWF0aW9uLmFkZFRpbWVsaW5lKGFuaW1hdGlvbik7XG4gICAgfVxuXG4gICAgZW5hYmxlQW5pbWF0aW9uKCl7XG4gICAgICAgIHRoaXMuX2FuaW1hdGlvbi5hdHRhY2hFdmVudHMoKTtcbiAgICB9XG5cbiAgICBkaXNhYmxlQW5pbWF0aW9uKCl7XG4gICAgICAgIHRoaXMuX2FuaW1hdGlvbi5kZXRhY2hFdmVudHMoKTtcbiAgICB9XG5cbiAgICBnZXRDb29yZGluYXRlcygpOiBDb29yZGluYXRlc3tcbiAgICAgICAgbGV0IGNhbnZhcyA9IHRoaXMudGh1bWJuYWlsQ2FudmFzIHx8IHRoaXMudmlkZW9DYW52YXM7XG4gICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICBsYXQ6IGNhbnZhcy5fbGF0LFxuICAgICAgICAgICAgbG9uOiBjYW52YXMuX2xvblxuICAgICAgICB9XG4gICAgfVxuXG4gICAgZ2V0IHRodW1ibmFpbENhbnZhcygpOiBCYXNlQ2FudmFzIHwgbnVsbHtcbiAgICAgICAgcmV0dXJuIHRoaXMuX3RodW1ibmFpbENhbnZhcztcbiAgICB9XG5cbiAgICBnZXQgdmlkZW9DYW52YXMoKTogQmFzZUNhbnZhc3tcbiAgICAgICAgcmV0dXJuIHRoaXMuX3ZpZGVvQ2FudmFzO1xuICAgIH1cblxuICAgIGdldCBwbGF5ZXIoKTogUGxheWVye1xuICAgICAgICByZXR1cm4gdGhpcy5fcGxheWVyO1xuICAgIH1cblxuICAgIGdldCBvcHRpb25zKCk6IFNldHRpbmdze1xuICAgICAgICByZXR1cm4gdGhpcy5fb3B0aW9ucztcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IFBhbm9yYW1hOyIsIi8vIEBmbG93XG5cbmltcG9ydCB0eXBlIHtQbGF5ZXIsIFNldHRpbmdzfSBmcm9tICcuL3R5cGVzJztcbmltcG9ydCBMb2FkZXIgZnJvbSAnLi90ZWNoL0xvYWRlcic7XG5pbXBvcnQgUGFub3JhbWEgZnJvbSAnLi9QYW5vcmFtYSc7XG5cbmxldCBwbGF5ZXJDbGFzczogQ2xhc3M8UGxheWVyPiB8IG51bGwgPSBMb2FkZXIod2luZG93LlZJREVPX1BBTk9SQU1BKTtcblxuaWYocGxheWVyQ2xhc3Mpe1xuICAgIHBsYXllckNsYXNzLnJlZ2lzdGVyUGx1Z2luKCk7XG59XG5lbHNle1xuICAgIHRocm93IG5ldyBFcnJvcihcIkNvdWxkIG5vdCBmb3VuZCBzdXBwb3J0IHBsYXllci5cIik7XG59XG5cbmNvbnN0IHBsdWdpbiA9IChwbGF5ZXJEb206IHN0cmluZyB8IEhUTUxWaWRlb0VsZW1lbnQsIG9wdGlvbnM6IFNldHRpbmdzKSA9PiB7XG4gICAgbGV0IHZpZGVvRW0gPSAodHlwZW9mIHBsYXllckRvbSA9PT0gXCJzdHJpbmdcIik/IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IocGxheWVyRG9tKTogcGxheWVyRG9tO1xuICAgIGlmKHBsYXllckNsYXNzKXtcbiAgICAgICAgLy8gJEZsb3dGaXhNZVxuICAgICAgICBsZXQgcGxheWVyID0gbmV3IHBsYXllckNsYXNzKHZpZGVvRW0sIG9wdGlvbnMpO1xuICAgICAgICBsZXQgcGFub3JhbWEgPSBuZXcgUGFub3JhbWEocGxheWVyLCBvcHRpb25zKTtcbiAgICAgICAgcmV0dXJuIHBhbm9yYW1hO1xuICAgIH1cbn07XG5cbndpbmRvdy5QYW5vcmFtYSA9IHBsdWdpbjtcblxuZXhwb3J0IGRlZmF1bHQgcGx1Z2luOyIsIi8vIEAgZmxvd1xuXG5pbXBvcnQgdHlwZSBDb21wb25lbnQgZnJvbSAnLi4vQ29tcG9uZW50cy9Db21wb25lbnQnO1xuaW1wb3J0IHR5cGUgeyBQbGF5ZXIsIENvbXBvbmVudERhdGEgfSBmcm9tICcuLi90eXBlcyc7XG5cbmNsYXNzIEJhc2VQbGF5ZXIgaW1wbGVtZW50cyBQbGF5ZXIge1xuICAgIF9jb21wb25lbnRzOiBBcnJheTxDb21wb25lbnREYXRhPjtcbiAgICBfdHJpZ2dlckNhbGxiYWNrOiBGdW5jdGlvbjtcblxuICAgIGNvbnN0cnVjdG9yKHBsYXllckluc3RhbmNlKXtcbiAgICAgICAgaWYgKE9iamVjdC5nZXRQcm90b3R5cGVPZih0aGlzKSA9PT0gQmFzZVBsYXllci5wcm90b3R5cGUpIHtcbiAgICAgICAgICAgIHRocm93IEVycm9yKCdhYnN0cmFjdCBjbGFzcyBzaG91bGQgbm90IGJlIGluc3RhbnRpYXRlZCBkaXJlY3RseTsgd3JpdGUgYSBzdWJjbGFzcycpO1xuICAgICAgICB9XG5cbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZSA9IHBsYXllckluc3RhbmNlO1xuICAgICAgICB0aGlzLl9jb21wb25lbnRzID0gW107XG4gICAgfVxuXG4gICAgc3RhdGljIHJlZ2lzdGVyUGx1Z2luKCl7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICByZWdpc3RlclRyaWdnZXJDYWxsYmFjayhjYWxsYmFjazogRnVuY3Rpb24pOiB2b2lke1xuICAgICAgICB0aGlzLl90cmlnZ2VyQ2FsbGJhY2sgPSBjYWxsYmFjaztcbiAgICB9XG5cbiAgICBlbCgpOiBIVE1MRWxlbWVudHtcbiAgICAgICAgdGhyb3cgRXJyb3IoJ05vdCBpbXBsZW1lbnRlZCcpO1xuICAgIH1cblxuICAgIGdldFZpZGVvRWwoKTogSFRNTFZpZGVvRWxlbWVudHtcbiAgICAgICAgdGhyb3cgRXJyb3IoJ05vdCBpbXBsZW1lbnRlZCcpO1xuICAgIH1cblxuICAgIGdldFRodW1ibmFpbFVSTCgpOiBzdHJpbmd7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICBvbiguLi5hcmdzOiBhbnkpOiB2b2lke1xuICAgICAgICB0aHJvdyBFcnJvcignTm90IGltcGxlbWVudGVkJyk7XG4gICAgfVxuXG4gICAgb2ZmKC4uLmFyZ3M6IGFueSk6IHZvaWR7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICBvbmUoLi4uYXJnczogYW55KTogdm9pZHtcbiAgICAgICAgdGhyb3cgRXJyb3IoJ05vdCBpbXBsZW1lbnRlZCcpO1xuICAgIH1cblxuICAgIHRyaWdnZXIobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhyb3cgRXJyb3IoJ05vdCBpbXBsZW1lbnRlZCcpO1xuICAgIH1cblxuICAgIGFkZENsYXNzKG5hbWU6IHN0cmluZyk6IHZvaWR7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICByZW1vdmVDbGFzcyhuYW1lOiBzdHJpbmcpOiB2b2lke1xuICAgICAgICB0aHJvdyBFcnJvcignTm90IGltcGxlbWVudGVkJyk7XG4gICAgfVxuXG4gICAgYWRkQ29tcG9uZW50KG5hbWU6IHN0cmluZywgY29tcG9uZW50OiBDb21wb25lbnQsIGxvY2F0aW9uOiA/SFRNTEVsZW1lbnQsIGluZGV4OiA/bnVtYmVyKTogQ29tcG9uZW50e1xuICAgICAgICBpZighbG9jYXRpb24pe1xuICAgICAgICAgICAgbG9jYXRpb24gPSB0aGlzLmVsKCk7XG4gICAgICAgIH1cbiAgICAgICAgaWYoIWluZGV4KXtcbiAgICAgICAgICAgIGluZGV4ID0gLTE7XG4gICAgICAgIH1cblxuICAgICAgICBpZih0eXBlb2YgY29tcG9uZW50LmVsID09PSBcImZ1bmN0aW9uXCIgJiYgY29tcG9uZW50LmVsKCkpe1xuICAgICAgICAgICAgaWYoaW5kZXggPT09IC0xKXtcbiAgICAgICAgICAgICAgICBsb2NhdGlvbi5hcHBlbmRDaGlsZChjb21wb25lbnQuZWwoKSk7XG4gICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICBsZXQgY2hpbGRyZW4gPSBsb2NhdGlvbi5jaGlsZE5vZGVzO1xuICAgICAgICAgICAgICAgIGxldCBjaGlsZCA9IGNoaWxkcmVuW2luZGV4XTtcbiAgICAgICAgICAgICAgICBsb2NhdGlvbi5pbnNlcnRCZWZvcmUoY29tcG9uZW50LmVsKCksIGNoaWxkKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgIHRoaXMuX2NvbXBvbmVudHMucHVzaCh7XG4gICAgICAgICAgICBuYW1lLFxuICAgICAgICAgICAgY29tcG9uZW50LFxuICAgICAgICAgICAgbG9jYXRpb25cbiAgICAgICAgfSk7XG5cbiAgICAgICAgcmV0dXJuIGNvbXBvbmVudDtcbiAgICB9XG5cbiAgICByZW1vdmVDb21wb25lbnQobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhpcy5fY29tcG9uZW50cyA9IHRoaXMuX2NvbXBvbmVudHMucmVkdWNlKChhY2MsIGNvbXBvbmVudCk9PntcbiAgICAgICAgICAgIGlmKGNvbXBvbmVudC5uYW1lICE9PSBuYW1lKXtcbiAgICAgICAgICAgICAgICBhY2MucHVzaChjb21wb25lbnQpXG4gICAgICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgICAgICBjb21wb25lbnQuY29tcG9uZW50LmRpc3Bvc2UoKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHJldHVybiBhY2M7XG4gICAgICAgIH0sIFtdKTtcbiAgICB9XG5cbiAgICBnZXRDb21wb25lbnQobmFtZTogc3RyaW5nKTogQ29tcG9uZW50IHwgbnVsbHtcbiAgICAgICAgbGV0IGNvbXBvbmVudERhdGE7XG4gICAgICAgIGZvcihsZXQgaSA9IDA7IGkgPCB0aGlzLl9jb21wb25lbnRzLmxlbmd0aDsgaSsrKXtcbiAgICAgICAgICAgIGlmKHRoaXMuX2NvbXBvbmVudHNbaV0ubmFtZSA9PT0gbmFtZSl7XG4gICAgICAgICAgICAgICAgY29tcG9uZW50RGF0YSA9IHRoaXMuX2NvbXBvbmVudHNbaV07XG4gICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGNvbXBvbmVudERhdGE/IGNvbXBvbmVudERhdGEuY29tcG9uZW50OiBudWxsO1xuICAgIH1cblxuICAgIHBsYXkoKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5wbGF5KCk7XG4gICAgfVxuXG4gICAgcGF1c2UoKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5wYXVzZSgpO1xuICAgIH1cblxuICAgIHBhdXNlZCgpOiBib29sZWFue1xuICAgICAgICB0aHJvdyBFcnJvcignTm90IGltcGxlbWVudGVkJyk7XG4gICAgfVxuXG4gICAgcmVhZHlTdGF0ZSgpOiBudW1iZXJ7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICByZXBvcnRVc2VyQWN0aXZpdHkoKTogdm9pZHtcbiAgICAgICAgdGhyb3cgRXJyb3IoJ05vdCBpbXBsZW1lbnRlZCcpO1xuICAgIH1cblxuICAgIGNvbnRyb2xCYXIoKTogSFRNTEVsZW1lbnR7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICBlbmFibGVGdWxsc2NyZWVuKCk6IHZvaWR7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICByZWFkeShmbjogRnVuY3Rpb24pOiB2b2lke1xuICAgICAgICB0aHJvdyBFcnJvcignTm90IGltcGxlbWVudGVkJyk7XG4gICAgfVxuXG4gICAgZ2V0IGNvbXBvbmVudHMoKTogQXJyYXk8Q29tcG9uZW50RGF0YT57XG4gICAgICAgIHJldHVybiB0aGlzLl9jb21wb25lbnRzO1xuICAgIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgQmFzZVBsYXllcjsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdHlwZSB7IFBsYXllciB9IGZyb20gJy4uL3R5cGVzJztcbmltcG9ydCBWaWRlb2pzNCBmcm9tICcuL1ZpZGVvanM0JztcbmltcG9ydCBWaWRlb2pzNSBmcm9tICcuL1ZpZGVvanM1JztcbmltcG9ydCBNZWRpYUVsZW1lbnQgZnJvbSAnLi9NZWRpYUVsZW1lbnRQbGF5ZXInO1xuaW1wb3J0IHsgZ2V0VmlkZW9qc1ZlcnNpb24sIHdhcm5pbmcgfSBmcm9tICcuLi91dGlscyc7XG5cbmNvbnN0IFZJREVPUExBWUVSID0ge1xuICAgICd2aWRlb2pzX3Y0JzogVmlkZW9qczQgLFxuICAgICd2aWRlb2pzX3Y1JyA6IFZpZGVvanM1LFxuICAgICdNZWRpYUVsZW1lbnRQbGF5ZXInOiBNZWRpYUVsZW1lbnRcbn07XG5cbmZ1bmN0aW9uIGNoZWNrVHlwZShwbGF5ZXJUeXBlOiBzdHJpbmcpOiBDbGFzczxQbGF5ZXI+IHwgbnVsbHtcbiAgICBpZih0eXBlb2YgcGxheWVyVHlwZSAhPT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgIGlmKFZJREVPUExBWUVSW3BsYXllclR5cGVdKXtcbiAgICAgICAgICAgIHJldHVybiBWSURFT1BMQVlFUltwbGF5ZXJUeXBlXTtcbiAgICAgICAgfVxuICAgICAgICB3YXJuaW5nKGBwbGF5ZXJUeXBlOiAke3BsYXllclR5cGV9IGlzIG5vdCBzdXBwb3J0ZWRgKTtcbiAgICB9XG4gICAgcmV0dXJuIG51bGw7XG59XG5cbmZ1bmN0aW9uIGNob29zZVRlY2goKTogQ2xhc3M8UGxheWVyPiB8IG51bGwge1xuICAgIGlmKHR5cGVvZiB3aW5kb3cudmlkZW9qcyAhPT0gXCJ1bmRlZmluZWRcIil7XG4gICAgICAgIGxldCB2ZXJzaW9uID0gd2luZG93LnZpZGVvanMuVkVSU0lPTjtcbiAgICAgICAgbGV0IG1ham9yID0gZ2V0VmlkZW9qc1ZlcnNpb24odmVyc2lvbik7XG4gICAgICAgIGlmKG1ham9yID09PSA0KXtcbiAgICAgICAgICAgIHJldHVybiBWSURFT1BMQVlFUlsndmlkZW9qc192NCddO1xuICAgICAgICB9ZWxzZXtcbiAgICAgICAgICAgIHJldHVybiBWSURFT1BMQVlFUlsndmlkZW9qc192NSddO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgaWYodHlwZW9mIHdpbmRvdy5NZWRpYUVsZW1lbnRQbGF5ZXIgIT09IFwidW5kZWZpbmVkXCIpe1xuICAgICAgICByZXR1cm4gVklERU9QTEFZRVJbXCJNZWRpYUVsZW1lbnRQbGF5ZXJcIl07XG4gICAgfVxuICAgIFxuICAgIHJldHVybiBudWxsO1xufVxuXG5mdW5jdGlvbiBMb2FkZXIocGxheWVyVHlwZTogc3RyaW5nKTogQ2xhc3M8UGxheWVyPiB8IG51bGx7XG4gICAgbGV0IHByZWZlclR5cGUgPSBjaGVja1R5cGUocGxheWVyVHlwZSk7XG4gICAgaWYoIXByZWZlclR5cGUpe1xuICAgICAgICBwcmVmZXJUeXBlID0gY2hvb3NlVGVjaCgpO1xuICAgIH1cblxuICAgIHJldHVybiBwcmVmZXJUeXBlO1xufVxuXG5cbmV4cG9ydCBkZWZhdWx0IExvYWRlcjsiLCIvLyBAIGZsb3dcblxuaW1wb3J0ICBQYW5vcmFtYSwgeyBkZWZhdWx0cyB9IGZyb20gJy4uL1Bhbm9yYW1hJztcbmltcG9ydCB7IG1lcmdlT3B0aW9ucywgY3VzdG9tRXZlbnQsIGlzSW9zIH0gZnJvbSAnLi4vdXRpbHMnO1xuaW1wb3J0IEJhc2VQbGF5ZXIgZnJvbSAnLi9CYXNlUGxheWVyJztcblxuY2xhc3MgTWVkaWFFbGVtZW50IGV4dGVuZHMgQmFzZVBsYXllcntcbiAgICBjb25zdHJ1Y3RvcihwbGF5ZXJJbnN0YW5jZTogYW55KXtcbiAgICAgICAgc3VwZXIocGxheWVySW5zdGFuY2UpO1xuICAgICAgICBpZihpc0lvcygpKXtcbiAgICAgICAgICAgIHRoaXMuX2Z1bGxzY3JlZW5PbklPUygpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgc3RhdGljIHJlZ2lzdGVyUGx1Z2luKCl7XG4gICAgICAgIG1lanMuTWVwRGVmYXVsdHMgPSBtZXJnZU9wdGlvbnMobWVqcy5NZXBEZWZhdWx0cywge1xuICAgICAgICAgICAgUGFub3JhbWE6IHtcbiAgICAgICAgICAgICAgICAuLi5kZWZhdWx0c1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcbiAgICAgICAgTWVkaWFFbGVtZW50UGxheWVyLnByb3RvdHlwZSA9IG1lcmdlT3B0aW9ucyhNZWRpYUVsZW1lbnRQbGF5ZXIucHJvdG90eXBlLCB7XG4gICAgICAgICAgICBidWlsZFBhbm9yYW1hKHBsYXllcil7XG4gICAgICAgICAgICAgICAgaWYocGxheWVyLmRvbU5vZGUudGFnTmFtZS50b0xvd2VyQ2FzZSgpICE9PSBcInZpZGVvXCIpe1xuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXCJQYW5vcmFtYSBkb24ndCBzdXBwb3J0IHRoaXJkIHBhcnR5IHBsYXllclwiKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgbGV0IGluc3RhbmNlID0gbmV3IE1lZGlhRWxlbWVudChwbGF5ZXIpO1xuICAgICAgICAgICAgICAgIHBsYXllci5wYW5vcmFtYSA9IG5ldyBQYW5vcmFtYShpbnN0YW5jZSwgdGhpcy5vcHRpb25zLlBhbm9yYW1hKTtcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICBjbGVhclBhbm9yYW1hKHBsYXllcil7XG4gICAgICAgICAgICAgICAgaWYocGxheWVyLnBhbm9yYW1hKXtcbiAgICAgICAgICAgICAgICAgICAgcGxheWVyLnBhbm9yYW1hLmRpc3Bvc2UoKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH0pXG4gICAgfVxuXG4gICAgZWwoKTogSFRNTEVsZW1lbnR7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRhaW5lcjtcbiAgICB9XG5cbiAgICBnZXRWaWRlb0VsKCk6IEhUTUxWaWRlb0VsZW1lbnR7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLmRvbU5vZGU7XG4gICAgfVxuXG4gICAgZ2V0VGh1bWJuYWlsVVJMKCk6IHN0cmluZ3tcbiAgICAgICByZXR1cm4gdGhpcy5wbGF5ZXJJbnN0YW5jZS5vcHRpb25zLnBvc3RlciB8fCB0aGlzLmdldFZpZGVvRWwoKS5nZXRBdHRyaWJ1dGUoXCJwb3N0ZXJcIik7XG4gICAgfVxuXG4gICAgYWRkQ2xhc3MobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5jb250YWluZXIuY2xhc3NMaXN0LmFkZChuYW1lKTtcbiAgICB9XG5cbiAgICByZW1vdmVDbGFzcyhuYW1lOiBzdHJpbmcpOiB2b2lke1xuICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRhaW5lci5jbGFzc0xpc3QucmVtb3ZlKG5hbWUpO1xuICAgIH1cblxuICAgIG9uKC4uLmFyZ3M6IGFueSk6IHZvaWR7XG4gICAgICAgIGxldCBuYW1lID0gYXJnc1swXTtcbiAgICAgICAgbGV0IGZuID0gYXJnc1sxXTtcbiAgICAgICAgdGhpcy5nZXRWaWRlb0VsKCkuYWRkRXZlbnRMaXN0ZW5lcihuYW1lLCBmbik7XG4gICAgfVxuXG4gICAgb2ZmKC4uLmFyZ3M6IGFueSk6IHZvaWR7XG4gICAgICAgIGxldCBuYW1lID0gYXJnc1swXTtcbiAgICAgICAgbGV0IGZuID0gYXJnc1sxXTtcbiAgICAgICAgdGhpcy5nZXRWaWRlb0VsKCkucmVtb3ZlRXZlbnRMaXN0ZW5lcihuYW1lLCBmbik7XG4gICAgfVxuXG4gICAgb25lKC4uLmFyZ3M6IGFueSk6IHZvaWR7XG4gICAgICAgIGxldCBuYW1lID0gYXJnc1swXTtcbiAgICAgICAgbGV0IGZuID0gYXJnc1sxXTtcbiAgICAgICAgbGV0IG9uZVRpbWVGdW5jdGlvbjtcbiAgICAgICAgdGhpcy5vbihuYW1lLCBvbmVUaW1lRnVuY3Rpb24gPSAoKT0+e1xuICAgICAgICAgICAgZm4oKTtcbiAgICAgICAgICAgIHRoaXMub2ZmKG5hbWUsIG9uZVRpbWVGdW5jdGlvbik7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIHRyaWdnZXIobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgbGV0IGV2ZW50ID0gY3VzdG9tRXZlbnQobmFtZSwgdGhpcy5lbCgpKTtcbiAgICAgICAgdGhpcy5nZXRWaWRlb0VsKCkuZGlzcGF0Y2hFdmVudChldmVudCk7XG4gICAgICAgIGlmKHRoaXMuX3RyaWdnZXJDYWxsYmFjayl7XG4gICAgICAgICAgICB0aGlzLl90cmlnZ2VyQ2FsbGJhY2sobmFtZSk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBwYXVzZWQoKTogYm9vbGVhbntcbiAgICAgICAgcmV0dXJuIHRoaXMuZ2V0VmlkZW9FbCgpLnBhdXNlZDtcbiAgICB9XG5cbiAgICByZWFkeVN0YXRlKCk6IG51bWJlcntcbiAgICAgICAgcmV0dXJuIHRoaXMuZ2V0VmlkZW9FbCgpLnJlYWR5U3RhdGU7XG4gICAgfVxuXG4gICAgcmVwb3J0VXNlckFjdGl2aXR5KCk6IHZvaWR7XG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2Uuc2hvd0NvbnRyb2xzKCk7XG4gICAgfVxuXG4gICAgY29udHJvbEJhcigpOiBIVE1MRWxlbWVudHtcbiAgICAgICAgcmV0dXJuIHRoaXMucGxheWVySW5zdGFuY2UuY29udHJvbHM7XG4gICAgfVxuXG4gICAgZW5hYmxlRnVsbHNjcmVlbigpOiB2b2lke1xuICAgICAgICBpZighdGhpcy5wbGF5ZXJJbnN0YW5jZS5pc0Z1bGxTY3JlZW4pe1xuICAgICAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5lbnRlckZ1bGxTY3JlZW4oKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIF9yZXNpemVDYW52YXNGbihjYW52YXM6IENvbXBvbmVudCk6IEZ1bmN0aW9ue1xuICAgICAgICByZXR1cm4gKCk9PntcbiAgICAgICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuY29udGFpbmVyLnN0eWxlLndpZHRoID0gXCIxMDAlXCI7XG4gICAgICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRhaW5lci5zdHlsZS5oZWlnaHQgPSBcIjEwMCVcIjtcbiAgICAgICAgICAgIGNhbnZhcy5oYW5kbGVSZXNpemUoKTtcbiAgICAgICAgfTtcbiAgICB9XG5cbiAgICBfZnVsbHNjcmVlbk9uSU9TKCl7XG4gICAgICAgIGxldCBzZWxmID0gdGhpcztcbiAgICAgICAgLy9kaXNhYmxlIGZ1bGxzY3JlZW4gb24gaW9zXG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuZW50ZXJGdWxsU2NyZWVuID0gZnVuY3Rpb24oKXtcbiAgICAgICAgICAgIGxldCBjYW52YXM6IENvbXBvbmVudCA9IHNlbGYuZ2V0Q29tcG9uZW50KFwiVmlkZW9DYW52YXNcIik7XG4gICAgICAgICAgICBsZXQgcmVzaXplRm4gPSBzZWxmLl9yZXNpemVDYW52YXNGbihjYW52YXMpLmJpbmQoc2VsZik7XG4gICAgICAgICAgICBzZWxmLnRyaWdnZXIoXCJiZWZvcmVfRW50ZXJGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgZG9jdW1lbnQuZG9jdW1lbnRFbGVtZW50LmNsYXNzTGlzdC5hZGQoYCR7dGhpcy5vcHRpb25zLmNsYXNzUHJlZml4fWZ1bGxzY3JlZW5gKTtcbiAgICAgICAgICAgIHNlbGYuYWRkQ2xhc3MoYCR7dGhpcy5vcHRpb25zLmNsYXNzUHJlZml4fWNvbnRhaW5lci1mdWxsc2NyZWVuYCk7XG4gICAgICAgICAgICB0aGlzLmNvbnRhaW5lci5zdHlsZS53aWR0aCA9IFwiMTAwJVwiO1xuICAgICAgICAgICAgdGhpcy5jb250YWluZXIuc3R5bGUuaGVpZ2h0ID0gXCIxMDAlXCI7XG4gICAgICAgICAgICB3aW5kb3cuYWRkRXZlbnRMaXN0ZW5lcihcImRldmljZW1vdGlvblwiLCByZXNpemVGbik7IC8vdHJpZ2dlciB3aGVuIHVzZXIgcm90YXRlIHNjcmVlblxuICAgICAgICAgICAgc2VsZi50cmlnZ2VyKFwiYWZ0ZXJfRW50ZXJGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgdGhpcy5pc0Z1bGxTY3JlZW4gPSB0cnVlO1xuICAgICAgICAgICAgY2FudmFzLmhhbmRsZVJlc2l6ZSgpO1xuICAgICAgICB9O1xuXG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuZXhpdEZ1bGxTY3JlZW4gPSBmdW5jdGlvbigpe1xuICAgICAgICAgICAgbGV0IGNhbnZhczogQ29tcG9uZW50ID0gc2VsZi5nZXRDb21wb25lbnQoXCJWaWRlb0NhbnZhc1wiKTtcbiAgICAgICAgICAgIGxldCByZXNpemVGbiA9IHNlbGYuX3Jlc2l6ZUNhbnZhc0ZuKGNhbnZhcykuYmluZChzZWxmKTtcbiAgICAgICAgICAgIHNlbGYudHJpZ2dlcihcImJlZm9yZV9FeGl0RnVsbHNjcmVlblwiKTtcbiAgICAgICAgICAgIGRvY3VtZW50LmRvY3VtZW50RWxlbWVudC5jbGFzc0xpc3QucmVtb3ZlKGAke3RoaXMub3B0aW9ucy5jbGFzc1ByZWZpeH1mdWxsc2NyZWVuYCk7XG4gICAgICAgICAgICBzZWxmLnJlbW92ZUNsYXNzKGAke3RoaXMub3B0aW9ucy5jbGFzc1ByZWZpeH1jb250YWluZXItZnVsbHNjcmVlbmApO1xuICAgICAgICAgICAgdGhpcy5pc0Z1bGxTY3JlZW4gPSBmYWxzZTtcbiAgICAgICAgICAgIHRoaXMuY29udGFpbmVyLnN0eWxlLndpZHRoID0gXCJcIjtcbiAgICAgICAgICAgIHRoaXMuY29udGFpbmVyLnN0eWxlLmhlaWdodCA9IFwiXCI7XG4gICAgICAgICAgICB3aW5kb3cucmVtb3ZlRXZlbnRMaXN0ZW5lcihcImRldmljZW1vdGlvblwiLCByZXNpemVGbik7XG4gICAgICAgICAgICBzZWxmLnRyaWdnZXIoXCJhZnRlcl9FeGl0RnVsbHNjcmVlblwiKTtcbiAgICAgICAgICAgIGNhbnZhcy5oYW5kbGVSZXNpemUoKTtcbiAgICAgICAgfTtcbiAgICB9XG5cbiAgICByZWFkeShmbjogRnVuY3Rpb24pOiB2b2lke1xuICAgICAgICB0aGlzLm9uZSgnY2FucGxheScsIGZuKTtcbiAgICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IE1lZGlhRWxlbWVudDsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdmlkZW9qcyBmcm9tICd2aWRlby5qcyc7XG5pbXBvcnQgQmFzZVZpZGVvSnMgZnJvbSAnLi92aWRlb2pzJztcbmltcG9ydCBQYW5vcmFtYSBmcm9tICcuLi9QYW5vcmFtYSc7XG5cbmNsYXNzIFZpZGVvanM0IGV4dGVuZHMgQmFzZVZpZGVvSnN7XG4gICAgc3RhdGljIHJlZ2lzdGVyUGx1Z2luKCk6IHZvaWR7XG4gICAgICAgIHZpZGVvanMucGx1Z2luKFwicGFub3JhbWFcIiwgZnVuY3Rpb24ob3B0aW9ucyl7XG4gICAgICAgICAgICBsZXQgaW5zdGFuY2UgPSBuZXcgVmlkZW9qczQodGhpcyk7XG4gICAgICAgICAgICBsZXQgcGFub3JhbWEgPSBuZXcgUGFub3JhbWEoaW5zdGFuY2UsIG9wdGlvbnMpO1xuICAgICAgICAgICAgcmV0dXJuIHBhbm9yYW1hO1xuICAgICAgICB9KTtcbiAgICB9XG5cbiAgICBnZXRWaWRlb0VsKCk6IEhUTUxWaWRlb0VsZW1lbnR7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLnRlY2g/XG4gICAgICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLnRlY2guZWwoKTpcbiAgICAgICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuaC5lbCgpO1xuICAgIH1cblxuICAgIF9vcmlnaW5hbEZ1bGxzY3JlZW5DbGlja0ZuKCl7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRyb2xCYXIuZnVsbHNjcmVlblRvZ2dsZS5vbkNsaWNrIHx8IHRoaXMucGxheWVySW5zdGFuY2UuY29udHJvbEJhci5mdWxsc2NyZWVuVG9nZ2xlLnU7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBWaWRlb2pzNDsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgdmlkZW9qcyBmcm9tICd2aWRlby5qcyc7XG5pbXBvcnQgQmFzZVZpZGVvSnMgZnJvbSAnLi92aWRlb2pzJztcbmltcG9ydCBQYW5vcmFtYSBmcm9tICcuLi9QYW5vcmFtYSc7XG5cbmNsYXNzIFZpZGVvanM1IGV4dGVuZHMgQmFzZVZpZGVvSnN7XG4gICAgc3RhdGljIHJlZ2lzdGVyUGx1Z2luKCk6IHZvaWR7XG4gICAgICAgIHZpZGVvanMucGx1Z2luKFwicGFub3JhbWFcIiwgZnVuY3Rpb24ob3B0aW9ucyl7XG4gICAgICAgICAgICBsZXQgaW5zdGFuY2UgPSBuZXcgVmlkZW9qczUodGhpcyk7XG4gICAgICAgICAgICBsZXQgcGFub3JhbWEgPSBuZXcgUGFub3JhbWEoaW5zdGFuY2UsIG9wdGlvbnMpO1xuICAgICAgICAgICAgcmV0dXJuIHBhbm9yYW1hO1xuICAgICAgICB9KTtcbiAgICB9XG5cbiAgICBnZXRWaWRlb0VsKCk6IEhUTUxWaWRlb0VsZW1lbnR7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLnRlY2goeyBJV2lsbE5vdFVzZVRoaXNJblBsdWdpbnM6IHRydWUgfSkuZWwoKTtcbiAgICB9XG5cbiAgICBfb3JpZ2luYWxGdWxsc2NyZWVuQ2xpY2tGbigpe1xuICAgICAgICByZXR1cm4gdGhpcy5wbGF5ZXJJbnN0YW5jZS5jb250cm9sQmFyLmZ1bGxzY3JlZW5Ub2dnbGUuaGFuZGxlQ2xpY2s7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBWaWRlb2pzNTsiLCIvLyBAZmxvd1xuXG5pbXBvcnQgQmFzZVBsYXllciBmcm9tICcuL0Jhc2VQbGF5ZXInO1xuaW1wb3J0IENvbXBvbmVudCBmcm9tICcuLi9Db21wb25lbnRzL0NvbXBvbmVudCc7XG5pbXBvcnQgeyBpc0lvcyB9IGZyb20gJy4uL3V0aWxzJztcblxuY2xhc3MgVmlkZW9qcyBleHRlbmRzIEJhc2VQbGF5ZXJ7XG4gICAgY29uc3RydWN0b3IocGxheWVySW5zdGFuY2U6IGFueSl7XG4gICAgICAgIHN1cGVyKHBsYXllckluc3RhbmNlKTtcbiAgICAgICAgLy9pb3MgZGV2aWNlIGRvbid0IHN1cHBvcnQgZnVsbHNjcmVlbiwgd2UgaGF2ZSB0byBtb25rZXkgcGF0Y2ggdGhlIG9yaWdpbmFsIGZ1bGxzY3JlZW4gZnVuY3Rpb24uXG4gICAgICAgIGlmKGlzSW9zKCkpe1xuICAgICAgICAgICAgdGhpcy5fZnVsbHNjcmVlbk9uSU9TKCk7XG4gICAgICAgIH1cbiAgICAgICAgLy9yZXNpemUgdmlkZW8gaWYgZnVsbHNjcmVlbiBjaGFuZ2UsIHRoaXMgaXMgdXNlZCBmb3IgaW9zIGRldmljZVxuICAgICAgICB0aGlzLm9uKFwiZnVsbHNjcmVlbmNoYW5nZVwiLCAgKCkgPT4ge1xuICAgICAgICAgICAgbGV0IGNhbnZhczogQ29tcG9uZW50ID0gdGhpcy5nZXRDb21wb25lbnQoXCJWaWRlb0NhbnZhc1wiKTtcbiAgICAgICAgICAgIGNhbnZhcy5oYW5kbGVSZXNpemUoKTtcbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgZWwoKTogSFRNTEVsZW1lbnR7XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLmVsKCk7XG4gICAgfVxuXG4gICAgZ2V0VmlkZW9FbCgpOiBIVE1MVmlkZW9FbGVtZW50e1xuICAgICAgICB0aHJvdyBFcnJvcignTm90IGltcGxlbWVudGVkJyk7XG4gICAgfVxuXG4gICAgZ2V0VGh1bWJuYWlsVVJMKCk6IHN0cmluZ3tcbiAgICAgICAgcmV0dXJuIHRoaXMucGxheWVySW5zdGFuY2UucG9zdGVyKCk7XG4gICAgfVxuXG4gICAgb24oLi4uYXJnczogYW55KTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5vbiguLi5hcmdzKTtcbiAgICB9XG5cbiAgICBvZmYoLi4uYXJnczogYW55KTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5vZmYoLi4uYXJncyk7XG4gICAgfVxuXG4gICAgb25lKC4uLmFyZ3M6IGFueSk6IHZvaWR7XG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2Uub25lKC4uLmFyZ3MpO1xuICAgIH1cblxuICAgIGFkZENsYXNzKG5hbWU6IHN0cmluZyk6IHZvaWR7XG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuYWRkQ2xhc3MobmFtZSk7XG4gICAgfVxuXG4gICAgcmVtb3ZlQ2xhc3MobmFtZTogc3RyaW5nKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5yZW1vdmVDbGFzcyhuYW1lKTtcbiAgICB9XG5cbiAgICBfcmVzaXplQ2FudmFzRm4oY2FudmFzOiBDb21wb25lbnQpOiBGdW5jdGlvbntcbiAgICAgICAgcmV0dXJuICgpPT57XG4gICAgICAgICAgICBjYW52YXMuaGFuZGxlUmVzaXplKCk7XG4gICAgICAgIH07XG4gICAgfVxuXG4gICAgcGF1c2VkKCk6IGJvb2xlYW57XG4gICAgICAgIHJldHVybiB0aGlzLnBsYXllckluc3RhbmNlLnBhdXNlZCgpO1xuICAgIH1cblxuICAgIHJlYWR5U3RhdGUoKTogbnVtYmVye1xuICAgICAgICByZXR1cm4gdGhpcy5wbGF5ZXJJbnN0YW5jZS5yZWFkeVN0YXRlKCk7XG4gICAgfVxuXG4gICAgdHJpZ2dlcihuYW1lOiBzdHJpbmcpOiB2b2lke1xuICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLnRyaWdnZXIobmFtZSk7XG4gICAgICAgIGlmKHRoaXMuX3RyaWdnZXJDYWxsYmFjayl7XG4gICAgICAgICAgICB0aGlzLl90cmlnZ2VyQ2FsbGJhY2sobmFtZSk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICByZXBvcnRVc2VyQWN0aXZpdHkoKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5yZXBvcnRVc2VyQWN0aXZpdHkoKTtcbiAgICB9XG5cbiAgICAvKipcbiAgICAgKiBHZXQgb3JpZ2luYWwgZnVsbHNjcmVlbiBmdW5jdGlvblxuICAgICAqL1xuICAgIF9vcmlnaW5hbEZ1bGxzY3JlZW5DbGlja0ZuKCl7XG4gICAgICAgIHRocm93IEVycm9yKCdOb3QgaW1wbGVtZW50ZWQnKTtcbiAgICB9XG5cbiAgICBfZnVsbHNjcmVlbk9uSU9TKCk6IHZvaWR7XG4gICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuY29udHJvbEJhci5mdWxsc2NyZWVuVG9nZ2xlLm9mZihcInRhcFwiLCB0aGlzLl9vcmlnaW5hbEZ1bGxzY3JlZW5DbGlja0ZuKCkpO1xuICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRyb2xCYXIuZnVsbHNjcmVlblRvZ2dsZS5vbihcInRhcFwiLCAoKSA9PiB7XG4gICAgICAgICAgICBsZXQgY2FudmFzOiBDb21wb25lbnQgPSB0aGlzLmdldENvbXBvbmVudChcIlZpZGVvQ2FudmFzXCIpO1xuICAgICAgICAgICAgbGV0IHJlc2l6ZUZuID0gdGhpcy5fcmVzaXplQ2FudmFzRm4oY2FudmFzKTtcbiAgICAgICAgICAgIGlmKCF0aGlzLnBsYXllckluc3RhbmNlLmlzRnVsbHNjcmVlbigpKXtcbiAgICAgICAgICAgICAgICB0aGlzLnRyaWdnZXIoXCJiZWZvcmVfRW50ZXJGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgICAgIC8vc2V0IHRvIGZ1bGxzY3JlZW5cbiAgICAgICAgICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmlzRnVsbHNjcmVlbih0cnVlKTtcbiAgICAgICAgICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmVudGVyRnVsbFdpbmRvdygpO1xuICAgICAgICAgICAgICAgIHdpbmRvdy5hZGRFdmVudExpc3RlbmVyKFwiZGV2aWNlbW90aW9uXCIsIHJlc2l6ZUZuKTsgLy90cmlnZ2VyIHdoZW4gdXNlciByb3RhdGUgc2NyZWVuXG4gICAgICAgICAgICAgICAgdGhpcy50cmlnZ2VyKFwiYWZ0ZXJfRW50ZXJGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgfWVsc2V7XG4gICAgICAgICAgICAgICAgdGhpcy50cmlnZ2VyKFwiYmVmb3JlX0V4aXRGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuaXNGdWxsc2NyZWVuKGZhbHNlKTtcbiAgICAgICAgICAgICAgICB0aGlzLnBsYXllckluc3RhbmNlLmV4aXRGdWxsV2luZG93KCk7XG4gICAgICAgICAgICAgICAgd2luZG93LnJlbW92ZUV2ZW50TGlzdGVuZXIoXCJkZXZpY2Vtb3Rpb25cIiwgcmVzaXplRm4pO1xuICAgICAgICAgICAgICAgIHRoaXMudHJpZ2dlcihcImFmdGVyX0V4aXRGdWxsc2NyZWVuXCIpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgdGhpcy50cmlnZ2VyKFwiZnVsbHNjcmVlbmNoYW5nZVwiKTtcbiAgICAgICAgfSk7XG4gICAgfVxuXG4gICAgY29udHJvbEJhcigpOiBIVE1MRWxlbWVudHtcbiAgICAgICAgbGV0IGNvbnRyb2xCYXIgPSB0aGlzLnBsYXllckluc3RhbmNlLmNvbnRyb2xCYXI7XG4gICAgICAgIHJldHVybiBjb250cm9sQmFyLmVsKCk7XG4gICAgfVxuXG4gICAgZW5hYmxlRnVsbHNjcmVlbigpOiB2b2lke1xuICAgICAgICBpZighdGhpcy5wbGF5ZXJJbnN0YW5jZS5pc0Z1bGxzY3JlZW4oKSlcbiAgICAgICAgICAgIHRoaXMucGxheWVySW5zdGFuY2UuY29udHJvbEJhci5mdWxsc2NyZWVuVG9nZ2xlLnRyaWdnZXIoXCJ0YXBcIik7XG4gICAgfVxuXG4gICAgcmVhZHkoZm46IEZ1bmN0aW9uKTogdm9pZHtcbiAgICAgICAgdGhpcy5wbGF5ZXJJbnN0YW5jZS5yZWFkeShmbik7XG4gICAgfVxufVxuXG5leHBvcnQgZGVmYXVsdCBWaWRlb2pzOyIsIi8vIEBmbG93XG5cbmZ1bmN0aW9uIHdoaWNoVHJhbnNpdGlvbkV2ZW50KCl7XG4gICAgbGV0IGVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnZGl2Jyk7XG4gICAgbGV0IHRyYW5zaXRpb25zID0ge1xuICAgICAgICAndHJhbnNpdGlvbic6J3RyYW5zaXRpb25lbmQnLFxuICAgICAgICAnT1RyYW5zaXRpb24nOidvVHJhbnNpdGlvbkVuZCcsXG4gICAgICAgICdNb3pUcmFuc2l0aW9uJzondHJhbnNpdGlvbmVuZCcsXG4gICAgICAgICdXZWJraXRUcmFuc2l0aW9uJzond2Via2l0VHJhbnNpdGlvbkVuZCdcbiAgICB9O1xuXG4gICAgZm9yKGxldCB0IGluIHRyYW5zaXRpb25zKXtcbiAgICAgICAgLy8gJEZsb3dGaXhNZVxuICAgICAgICBpZiggZWwuc3R5bGVbdF0gIT09IHVuZGVmaW5lZCApe1xuICAgICAgICAgICAgcmV0dXJuIHRyYW5zaXRpb25zW3RdO1xuICAgICAgICB9XG4gICAgfVxufVxuXG5leHBvcnQgY29uc3QgdHJhbnNpdGlvbkV2ZW50ID0gd2hpY2hUcmFuc2l0aW9uRXZlbnQoKTtcblxuLy9hZG9wdCBmcm9tIGh0dHA6Ly9naXptYS5jb20vZWFzaW5nL1xuZnVuY3Rpb24gbGluZWFyKHQ6IG51bWJlciwgYjogbnVtYmVyLCBjOiBudW1iZXIsIGQ6IG51bWJlcik6IG51bWJlcntcbiAgICByZXR1cm4gYyp0L2QgKyBiO1xufVxuXG5mdW5jdGlvbiBlYXNlSW5RdWFkKHQ6IG51bWJlciwgYjogbnVtYmVyLCBjOiBudW1iZXIsIGQ6IG51bWJlcik6IG51bWJlciB7XG4gICAgdCAvPSBkO1xuICAgIHJldHVybiBjKnQqdCArIGI7XG59XG5cbmZ1bmN0aW9uIGVhc2VPdXRRdWFkKHQ6IG51bWJlciwgYjogbnVtYmVyLCBjOiBudW1iZXIsIGQ6IG51bWJlcik6IG51bWJlciB7XG4gICAgdCAvPSBkO1xuICAgIHJldHVybiAtYyAqIHQqKHQtMikgKyBiO1xufVxuXG5mdW5jdGlvbiBlYXNlSW5PdXRRdWFkKHQ6IG51bWJlciwgYjogbnVtYmVyLCBjOiBudW1iZXIsIGQ6IG51bWJlcik6IG51bWJlciB7XG4gICAgdCAvPSBkIC8gMjtcbiAgICBpZiAodCA8IDEpIHJldHVybiBjIC8gMiAqIHQgKiB0ICsgYjtcbiAgICB0LS07XG4gICAgcmV0dXJuIC1jIC8gMiAqICh0ICogKHQgLSAyKSAtIDEpICsgYjtcbn1cblxuZXhwb3J0IGNvbnN0IGVhc2VGdW5jdGlvbnMgPSB7XG4gICAgbGluZWFyOiBsaW5lYXIsXG4gICAgZWFzZUluUXVhZDogZWFzZUluUXVhZCxcbiAgICBlYXNlT3V0UXVhZDogZWFzZU91dFF1YWQsXG4gICAgZWFzZUluT3V0UXVhZDogZWFzZUluT3V0UXVhZFxufTsiLCIvLyBAZmxvd1xuXG5jbGFzcyBfRGV0ZWN0b3Ige1xuICAgIGNhbnZhczogSFRNTENhbnZhc0VsZW1lbnQ7XG4gICAgd2ViZ2w6IGJvb2xlYW47XG4gICAgd29ya2VyczogV29ya2VyO1xuICAgIGZpbGVhcGk6IEZpbGU7XG5cbiAgICBjb25zdHJ1Y3Rvcigpe1xuICAgICAgICB0aGlzLmNhbnZhcyA9ICEhd2luZG93LkNhbnZhc1JlbmRlcmluZ0NvbnRleHQyRDtcbiAgICAgICAgdGhpcy53ZWJnbCA9IGZhbHNlO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgdGhpcy5jYW52YXMgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KFwiY2FudmFzXCIpO1xuICAgICAgICAgICAgdGhpcy53ZWJnbCA9ICEhICggd2luZG93LldlYkdMUmVuZGVyaW5nQ29udGV4dCAmJiAoIHRoaXMuY2FudmFzLmdldENvbnRleHQoICd3ZWJnbCcgKSB8fCB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCAnZXhwZXJpbWVudGFsLXdlYmdsJyApICkgKVxuICAgICAgICB9XG4gICAgICAgIGNhdGNoKGUpe1xuICAgICAgICB9XG4gICAgICAgIHRoaXMud29ya2VycyA9ICEhd2luZG93LldvcmtlcjtcbiAgICAgICAgdGhpcy5maWxlYXBpID0gd2luZG93LkZpbGUgJiYgd2luZG93LkZpbGVSZWFkZXIgJiYgd2luZG93LkZpbGVMaXN0ICYmIHdpbmRvdy5CbG9iO1xuICAgIH1cbn1cblxuZXhwb3J0IGNvbnN0IERldGVjdG9yID0gIG5ldyBfRGV0ZWN0b3IoKTtcblxuZXhwb3J0IGZ1bmN0aW9uIHdlYkdMRXJyb3JNZXNzYWdlKCk6IEhUTUxFbGVtZW50IHtcbiAgICBsZXQgZWxlbWVudCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoICdkaXYnICk7XG4gICAgZWxlbWVudC5pZCA9ICd3ZWJnbC1lcnJvci1tZXNzYWdlJztcblxuICAgIGlmICggISBEZXRlY3Rvci53ZWJnbCApIHtcbiAgICAgICAgZWxlbWVudC5pbm5lckhUTUwgPSB3aW5kb3cuV2ViR0xSZW5kZXJpbmdDb250ZXh0ID8gW1xuICAgICAgICAgICAgJ1lvdXIgZ3JhcGhpY3MgY2FyZCBkb2VzIG5vdCBzZWVtIHRvIHN1cHBvcnQgPGEgaHJlZj1cImh0dHA6Ly9raHJvbm9zLm9yZy93ZWJnbC93aWtpL0dldHRpbmdfYV9XZWJHTF9JbXBsZW1lbnRhdGlvblwiIHN0eWxlPVwiY29sb3I6IzAwMFwiPldlYkdMPC9hPi48YnIgLz4nLFxuICAgICAgICAgICAgJ0ZpbmQgb3V0IGhvdyB0byBnZXQgaXQgPGEgaHJlZj1cImh0dHA6Ly9nZXQud2ViZ2wub3JnL1wiIHN0eWxlPVwiY29sb3I6IzAwMFwiPmhlcmU8L2E+LidcbiAgICAgICAgXS5qb2luKCAnXFxuJyApIDogW1xuICAgICAgICAgICAgJ1lvdXIgYnJvd3NlciBkb2VzIG5vdCBzZWVtIHRvIHN1cHBvcnQgPGEgaHJlZj1cImh0dHA6Ly9raHJvbm9zLm9yZy93ZWJnbC93aWtpL0dldHRpbmdfYV9XZWJHTF9JbXBsZW1lbnRhdGlvblwiIHN0eWxlPVwiY29sb3I6IzAwMFwiPldlYkdMPC9hPi48YnIvPicsXG4gICAgICAgICAgICAnRmluZCBvdXQgaG93IHRvIGdldCBpdCA8YSBocmVmPVwiaHR0cDovL2dldC53ZWJnbC5vcmcvXCIgc3R5bGU9XCJjb2xvcjojMDAwXCI+aGVyZTwvYT4uJ1xuICAgICAgICBdLmpvaW4oICdcXG4nICk7XG4gICAgfVxuICAgIHJldHVybiBlbGVtZW50O1xufVxuXG4vKipcbiAqIGNoZWNrIGllIG9yIGVkZ2UgYnJvd3NlciB2ZXJzaW9uLCByZXR1cm4gLTEgaWYgdXNlIG90aGVyIGJyb3dzZXJzXG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBpZU9yRWRnZVZlcnNpb24oKXtcbiAgICBsZXQgcnYgPSAtMTtcbiAgICBpZiAobmF2aWdhdG9yLmFwcE5hbWUgPT09ICdNaWNyb3NvZnQgSW50ZXJuZXQgRXhwbG9yZXInKSB7XG5cbiAgICAgICAgbGV0IHVhID0gbmF2aWdhdG9yLnVzZXJBZ2VudCxcbiAgICAgICAgICAgIHJlID0gbmV3IFJlZ0V4cChcIk1TSUUgKFswLTldezEsfVtcXFxcLjAtOV17MCx9KVwiKTtcblxuICAgICAgICBpZiAocmUuZXhlYyh1YSkgIT09IG51bGwpIHtcbiAgICAgICAgICAgIC8vICRGbG93Rml4TWU6IHN1cHByZXNzaW5nIHRoaXMgZXJyb3IsIFJlZ0V4cCBkb24ndCBzdXBwb3J0IHN0YXRpYyBwcm9wZXJ0eVxuICAgICAgICAgICAgcnYgPSBwYXJzZUZsb2F0KFJlZ0V4cC4kMSk7XG4gICAgICAgIH1cbiAgICB9XG4gICAgZWxzZSBpZiAobmF2aWdhdG9yLmFwcE5hbWUgPT09IFwiTmV0c2NhcGVcIikge1xuICAgICAgICAvLy8gaW4gSUUgMTEgdGhlIG5hdmlnYXRvci5hcHBWZXJzaW9uIHNheXMgJ3RyaWRlbnQnXG4gICAgICAgIC8vLyBpbiBFZGdlIHRoZSBuYXZpZ2F0b3IuYXBwVmVyc2lvbiBkb2VzIG5vdCBzYXkgdHJpZGVudFxuICAgICAgICBpZiAobmF2aWdhdG9yLmFwcFZlcnNpb24uaW5kZXhPZignVHJpZGVudCcpICE9PSAtMSkgcnYgPSAxMTtcbiAgICAgICAgZWxzZXtcbiAgICAgICAgICAgIGxldCB1YSA9IG5hdmlnYXRvci51c2VyQWdlbnQ7XG4gICAgICAgICAgICBsZXQgcmUgPSBuZXcgUmVnRXhwKFwiRWRnZVxcLyhbMC05XXsxLH1bXFxcXC4wLTldezAsfSlcIik7XG4gICAgICAgICAgICBpZiAocmUuZXhlYyh1YSkgIT09IG51bGwpIHtcbiAgICAgICAgICAgICAgICAvLyAkRmxvd0ZpeE1lXG4gICAgICAgICAgICAgICAgcnYgPSBwYXJzZUZsb2F0KFJlZ0V4cC4kMSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICByZXR1cm4gcnY7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBpc0xpdmVTdHJlYW1PblNhZmFyaSh2aWRlb0VsZW1lbnQ6IEhUTUxWaWRlb0VsZW1lbnQpe1xuICAgIC8vbGl2ZSBzdHJlYW0gb24gc2FmYXJpIGRvZXNuJ3Qgc3VwcG9ydCB2aWRlbyB0ZXh0dXJlXG4gICAgbGV0IHZpZGVvU291cmNlcyA9IFtdLnNsaWNlLmNhbGwodmlkZW9FbGVtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzb3VyY2VcIikpO1xuICAgIGxldCByZXN1bHQgPSBmYWxzZTtcbiAgICBpZih2aWRlb0VsZW1lbnQuc3JjICYmIHZpZGVvRWxlbWVudC5zcmMuaW5kZXhPZignLm0zdTgnKSA+IC0xKXtcbiAgICAgICAgdmlkZW9Tb3VyY2VzLnB1c2goe1xuICAgICAgICAgICAgc3JjOiB2aWRlb0VsZW1lbnQuc3JjLFxuICAgICAgICAgICAgdHlwZTogXCJhcHBsaWNhdGlvbi94LW1wZWdVUkxcIlxuICAgICAgICB9KTtcbiAgICB9XG4gICAgZm9yKGxldCBpID0gMDsgaSA8IHZpZGVvU291cmNlcy5sZW5ndGg7IGkrKyl7XG4gICAgICAgIGxldCBjdXJyZW50VmlkZW9Tb3VyY2UgPSB2aWRlb1NvdXJjZXNbaV07XG4gICAgICAgIGlmKChjdXJyZW50VmlkZW9Tb3VyY2UudHlwZSA9PT0gXCJhcHBsaWNhdGlvbi94LW1wZWdVUkxcIiB8fCBjdXJyZW50VmlkZW9Tb3VyY2UudHlwZSA9PT0gXCJhcHBsaWNhdGlvbi92bmQuYXBwbGUubXBlZ3VybFwiKSAmJiAvKFNhZmFyaXxBcHBsZVdlYktpdCkvLnRlc3QobmF2aWdhdG9yLnVzZXJBZ2VudCkgJiYgL0FwcGxlIENvbXB1dGVyLy50ZXN0KG5hdmlnYXRvci52ZW5kb3IpKXtcbiAgICAgICAgICAgIHJlc3VsdCA9IHRydWU7XG4gICAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gcmVzdWx0O1xufVxuXG5leHBvcnQgZnVuY3Rpb24gc3VwcG9ydFZpZGVvVGV4dHVyZSh2aWRlb0VsZW1lbnQ6IEhUTUxWaWRlb0VsZW1lbnQpe1xuICAgIC8vaWUgMTEgYW5kIGVkZ2UgMTIgYW5kIGxpdmUgc3RyZWFtIG9uIHNhZmFyaSBkb2Vzbid0IHN1cHBvcnQgdmlkZW8gdGV4dHVyZSBkaXJlY3RseS5cbiAgICBsZXQgdmVyc2lvbiA9IGllT3JFZGdlVmVyc2lvbigpO1xuICAgIHJldHVybiAodmVyc2lvbiA9PT0gLTEgfHwgdmVyc2lvbiA+PSAxMykgJiYgIWlzTGl2ZVN0cmVhbU9uU2FmYXJpKHZpZGVvRWxlbWVudCk7XG59XG5cbiIsIi8vIEBmbG93XG5cbmV4cG9ydCBmdW5jdGlvbiBjdXN0b21FdmVudChldmVudE5hbWU6IHN0cmluZywgdGFyZ2V0OiBIVE1MRWxlbWVudCk6IEN1c3RvbUV2ZW50e1xuICAgIGxldCBldmVudCA9IG5ldyBDdXN0b21FdmVudChldmVudE5hbWUsIHtcbiAgICAgICAgJ2RldGFpbCc6IHtcbiAgICAgICAgICAgIHRhcmdldFxuICAgICAgICB9XG4gICAgfSk7XG4gICAgcmV0dXJuIGV2ZW50O1xufSIsIi8vIEBmbG93XG5cbmV4cG9ydCAqIGZyb20gJy4vbWVyZ2Utb3B0aW9ucyc7XG5leHBvcnQgKiBmcm9tICcuL3dhcm5pbmcnO1xuZXhwb3J0ICogZnJvbSAnLi9kZXRlY3Rvcic7XG5leHBvcnQgKiBmcm9tICcuL3ZlcnNpb24nO1xuZXhwb3J0ICogZnJvbSAnLi9tb2JpbGUnO1xuZXhwb3J0ICogZnJvbSAnLi92cic7XG5leHBvcnQgKiBmcm9tICcuL2FuaW1hdGlvbic7XG5leHBvcnQgKiBmcm9tICcuL2V2ZW50JzsiLCIvLyBAZmxvd1xuXG4vKipcbiAqIGNvZGUgYWRvcHQgZnJvbSBodHRwczovL2dpdGh1Yi5jb20vdmlkZW9qcy92aWRlby5qcy9ibG9iL21hc3Rlci9zcmMvanMvdXRpbHMvbWVyZ2Utb3B0aW9ucy5qc1xuICovXG5cbi8qKlxuICogUmV0dXJucyB3aGV0aGVyIGEgdmFsdWUgaXMgYW4gb2JqZWN0IG9mIGFueSBraW5kIC0gaW5jbHVkaW5nIERPTSBub2RlcyxcbiAqIGFycmF5cywgcmVndWxhciBleHByZXNzaW9ucywgZXRjLiBOb3QgZnVuY3Rpb25zLCB0aG91Z2guXG4gKlxuICogVGhpcyBhdm9pZHMgdGhlIGdvdGNoYSB3aGVyZSB1c2luZyBgdHlwZW9mYCBvbiBhIGBudWxsYCB2YWx1ZVxuICogcmVzdWx0cyBpbiBgJ29iamVjdCdgLlxuICpcbiAqIEBwYXJhbSAge09iamVjdH0gdmFsdWVcbiAqIEByZXR1cm4ge0Jvb2xlYW59XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBpc09iamVjdCh2YWx1ZTogYW55KSB7XG4gICAgcmV0dXJuICEhdmFsdWUgJiYgdHlwZW9mIHZhbHVlID09PSAnb2JqZWN0Jztcbn1cblxuLyoqXG4gKiBSZXR1cm5zIHdoZXRoZXIgYW4gb2JqZWN0IGFwcGVhcnMgdG8gYmUgYSBcInBsYWluXCIgb2JqZWN0IC0gdGhhdCBpcywgYVxuICogZGlyZWN0IGluc3RhbmNlIG9mIGBPYmplY3RgLlxuICpcbiAqIEBwYXJhbSAge09iamVjdH0gdmFsdWVcbiAqIEByZXR1cm4ge0Jvb2xlYW59XG4gKi9cbmV4cG9ydCBmdW5jdGlvbiBpc1BsYWluKHZhbHVlOiBhbnkpIHtcbiAgICByZXR1cm4gaXNPYmplY3QodmFsdWUpICYmXG4gICAgICAgIE9iamVjdC5wcm90b3R5cGUudG9TdHJpbmcuY2FsbCh2YWx1ZSkgPT09ICdbb2JqZWN0IE9iamVjdF0nICYmXG4gICAgICAgIHZhbHVlLmNvbnN0cnVjdG9yID09PSBPYmplY3Q7XG59XG5cbmV4cG9ydCBjb25zdCBtZXJnZU9wdGlvbnMgPSAoLi4uc291cmNlczogYW55KTogYW55ID0+IHtcbiAgICBsZXQgcmVzdWx0cyA9IHt9O1xuICAgIHNvdXJjZXMuZm9yRWFjaCgodmFsdWVzKT0+e1xuICAgICAgICBpZiAoIXZhbHVlcykge1xuICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICB9XG5cbiAgICAgICAgT2JqZWN0LmdldE93blByb3BlcnR5TmFtZXModmFsdWVzKS5mb3JFYWNoKChrZXkpPT57XG4gICAgICAgICAgICBsZXQgdmFsdWUgPSB2YWx1ZXNba2V5XTtcbiAgICAgICAgICAgIGlmICghaXNQbGFpbih2YWx1ZSkpIHtcbiAgICAgICAgICAgICAgICByZXN1bHRzW2tleV0gPSB2YWx1ZTtcbiAgICAgICAgICAgICAgICByZXR1cm47XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIGlmICghaXNQbGFpbihyZXN1bHRzW2tleV0pKSB7XG4gICAgICAgICAgICAgICAgcmVzdWx0c1trZXldID0ge307XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIHJlc3VsdHNba2V5XSA9IG1lcmdlT3B0aW9ucyhyZXN1bHRzW2tleV0sIHZhbHVlKTtcbiAgICAgICAgfSk7XG4gICAgfSk7XG5cbiAgICByZXR1cm4gcmVzdWx0cztcbn07IiwiLy8gQGZsb3dcblxuZXhwb3J0IGZ1bmN0aW9uIGdldFRvdWNoZXNEaXN0YW5jZSh0b3VjaGVzOiBhbnkpOiBudW1iZXJ7XG4gICAgcmV0dXJuIE1hdGguc3FydChcbiAgICAgICAgKHRvdWNoZXNbMF0uY2xpZW50WC10b3VjaGVzWzFdLmNsaWVudFgpICogKHRvdWNoZXNbMF0uY2xpZW50WC10b3VjaGVzWzFdLmNsaWVudFgpICtcbiAgICAgICAgKHRvdWNoZXNbMF0uY2xpZW50WS10b3VjaGVzWzFdLmNsaWVudFkpICogKHRvdWNoZXNbMF0uY2xpZW50WS10b3VjaGVzWzFdLmNsaWVudFkpKTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIG1vYmlsZUFuZFRhYmxldGNoZWNrKCkge1xuICAgIGxldCBjaGVjazogYm9vbGVhbiA9IGZhbHNlO1xuICAgIChmdW5jdGlvbihhKXtcbiAgICAgICAgICAgIGlmKC8oYW5kcm9pZHxiYlxcZCt8bWVlZ28pLittb2JpbGV8YXZhbnRnb3xiYWRhXFwvfGJsYWNrYmVycnl8YmxhemVyfGNvbXBhbHxlbGFpbmV8ZmVubmVjfGhpcHRvcHxpZW1vYmlsZXxpcChob25lfG9kKXxpcmlzfGtpbmRsZXxsZ2UgfG1hZW1vfG1pZHB8bW1wfG1vYmlsZS4rZmlyZWZveHxuZXRmcm9udHxvcGVyYSBtKG9ifGluKWl8cGFsbSggb3MpP3xwaG9uZXxwKGl4aXxyZSlcXC98cGx1Y2tlcnxwb2NrZXR8cHNwfHNlcmllcyg0fDYpMHxzeW1iaWFufHRyZW98dXBcXC4oYnJvd3NlcnxsaW5rKXx2b2RhZm9uZXx3YXB8d2luZG93cyBjZXx4ZGF8eGlpbm98YW5kcm9pZHxpcGFkfHBsYXlib29rfHNpbGsvaS50ZXN0KGEpfHwvMTIwN3w2MzEwfDY1OTB8M2dzb3w0dGhwfDUwWzEtNl1pfDc3MHN8ODAyc3xhIHdhfGFiYWN8YWMoZXJ8b298c1xcLSl8YWkoa298cm4pfGFsKGF2fGNhfGNvKXxhbW9pfGFuKGV4fG55fHl3KXxhcHR1fGFyKGNofGdvKXxhcyh0ZXx1cyl8YXR0d3xhdShkaXxcXC1tfHIgfHMgKXxhdmFufGJlKGNrfGxsfG5xKXxiaShsYnxyZCl8YmwoYWN8YXopfGJyKGV8dil3fGJ1bWJ8YndcXC0obnx1KXxjNTVcXC98Y2FwaXxjY3dhfGNkbVxcLXxjZWxsfGNodG18Y2xkY3xjbWRcXC18Y28obXB8bmQpfGNyYXd8ZGEoaXR8bGx8bmcpfGRidGV8ZGNcXC1zfGRldml8ZGljYXxkbW9ifGRvKGN8cClvfGRzKDEyfFxcLWQpfGVsKDQ5fGFpKXxlbShsMnx1bCl8ZXIoaWN8azApfGVzbDh8ZXooWzQtN10wfG9zfHdhfHplKXxmZXRjfGZseShcXC18Xyl8ZzEgdXxnNTYwfGdlbmV8Z2ZcXC01fGdcXC1tb3xnbyhcXC53fG9kKXxncihhZHx1bil8aGFpZXxoY2l0fGhkXFwtKG18cHx0KXxoZWlcXC18aGkocHR8dGEpfGhwKCBpfGlwKXxoc1xcLWN8aHQoYyhcXC18IHxffGF8Z3xwfHN8dCl8dHApfGh1KGF3fHRjKXxpXFwtKDIwfGdvfG1hKXxpMjMwfGlhYyggfFxcLXxcXC8pfGlicm98aWRlYXxpZzAxfGlrb218aW0xa3xpbm5vfGlwYXF8aXJpc3xqYSh0fHYpYXxqYnJvfGplbXV8amlnc3xrZGRpfGtlaml8a2d0KCB8XFwvKXxrbG9ufGtwdCB8a3djXFwtfGt5byhjfGspfGxlKG5vfHhpKXxsZyggZ3xcXC8oa3xsfHUpfDUwfDU0fFxcLVthLXddKXxsaWJ3fGx5bnh8bTFcXC13fG0zZ2F8bTUwXFwvfG1hKHRlfHVpfHhvKXxtYygwMXwyMXxjYSl8bVxcLWNyfG1lKHJjfHJpKXxtaShvOHxvYXx0cyl8bW1lZnxtbygwMXwwMnxiaXxkZXxkb3x0KFxcLXwgfG98dil8enopfG10KDUwfHAxfHYgKXxtd2JwfG15d2F8bjEwWzAtMl18bjIwWzItM118bjMwKDB8Mil8bjUwKDB8Mnw1KXxuNygwKDB8MSl8MTApfG5lKChjfG0pXFwtfG9ufHRmfHdmfHdnfHd0KXxub2soNnxpKXxuenBofG8yaW18b3AodGl8d3YpfG9yYW58b3dnMXxwODAwfHBhbihhfGR8dCl8cGR4Z3xwZygxM3xcXC0oWzEtOF18YykpfHBoaWx8cGlyZXxwbChheXx1Yyl8cG5cXC0yfHBvKGNrfHJ0fHNlKXxwcm94fHBzaW98cHRcXC1nfHFhXFwtYXxxYygwN3wxMnwyMXwzMnw2MHxcXC1bMi03XXxpXFwtKXxxdGVrfHIzODB8cjYwMHxyYWtzfHJpbTl8cm8odmV8em8pfHM1NVxcL3xzYShnZXxtYXxtbXxtc3xueXx2YSl8c2MoMDF8aFxcLXxvb3xwXFwtKXxzZGtcXC98c2UoYyhcXC18MHwxKXw0N3xtY3xuZHxyaSl8c2doXFwtfHNoYXJ8c2llKFxcLXxtKXxza1xcLTB8c2woNDV8aWQpfHNtKGFsfGFyfGIzfGl0fHQ1KXxzbyhmdHxueSl8c3AoMDF8aFxcLXx2XFwtfHYgKXxzeSgwMXxtYil8dDIoMTh8NTApfHQ2KDAwfDEwfDE4KXx0YShndHxsayl8dGNsXFwtfHRkZ1xcLXx0ZWwoaXxtKXx0aW1cXC18dFxcLW1vfHRvKHBsfHNoKXx0cyg3MHxtXFwtfG0zfG01KXx0eFxcLTl8dXAoXFwuYnxnMXxzaSl8dXRzdHx2NDAwfHY3NTB8dmVyaXx2aShyZ3x0ZSl8dmsoNDB8NVswLTNdfFxcLXYpfHZtNDB8dm9kYXx2dWxjfHZ4KDUyfDUzfDYwfDYxfDcwfDgwfDgxfDgzfDg1fDk4KXx3M2MoXFwtfCApfHdlYmN8d2hpdHx3aShnIHxuY3xudyl8d21sYnx3b251fHg3MDB8eWFzXFwtfHlvdXJ8emV0b3x6dGVcXC0vaS50ZXN0KGEuc3Vic3RyKDAsNCkpKVxuICAgICAgICAgICAgICAgIGNoZWNrID0gdHJ1ZVxuICAgICAgICB9KShuYXZpZ2F0b3IudXNlckFnZW50fHxuYXZpZ2F0b3IudmVuZG9yfHx3aW5kb3cub3BlcmEpO1xuICAgIHJldHVybiBjaGVjaztcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGlzSW9zKCkge1xuICAgIHJldHVybiAvaVBob25lfGlQYWR8aVBvZC9pLnRlc3QobmF2aWdhdG9yLnVzZXJBZ2VudCk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBpc1JlYWxJcGhvbmUoKSB7XG4gICAgcmV0dXJuIC9pUGhvbmV8aVBvZC9pLnRlc3QobmF2aWdhdG9yLnBsYXRmb3JtKTtcbn0iLCIvLyBAZmxvd1xuXG5leHBvcnQgZnVuY3Rpb24gZ2V0VmlkZW9qc1ZlcnNpb24oc3RyOiBzdHJpbmcpe1xuICAgIGxldCBpbmRleCA9IHN0ci5pbmRleE9mKFwiLlwiKTtcbiAgICBpZihpbmRleCA9PT0gLTEpIHJldHVybiAwO1xuICAgIGxldCBtYWpvciA9IHBhcnNlSW50KHN0ci5zdWJzdHJpbmcoMCwgaW5kZXgpKTtcbiAgICByZXR1cm4gbWFqb3I7XG59IiwiLy8gQGZsb3dcblxuaW1wb3J0IFRIUkVFIGZyb20gXCJ0aHJlZVwiO1xuXG4vL2Fkb3B0IGNvZGUgZnJvbTogaHR0cHM6Ly9naXRodWIuY29tL01velZSL3ZyLXdlYi1leGFtcGxlcy9ibG9iL21hc3Rlci90aHJlZWpzLXZyLWJvaWxlcnBsYXRlL2pzL1ZSRWZmZWN0LmpzXG5mdW5jdGlvbiBmb3ZUb05EQ1NjYWxlT2Zmc2V0KCBmb3Y6IGFueSApIHtcbiAgICBsZXQgcHhzY2FsZSA9IDIuMCAvIChmb3YubGVmdFRhbiArIGZvdi5yaWdodFRhbik7XG4gICAgbGV0IHB4b2Zmc2V0ID0gKGZvdi5sZWZ0VGFuIC0gZm92LnJpZ2h0VGFuKSAqIHB4c2NhbGUgKiAwLjU7XG4gICAgbGV0IHB5c2NhbGUgPSAyLjAgLyAoZm92LnVwVGFuICsgZm92LmRvd25UYW4pO1xuICAgIGxldCBweW9mZnNldCA9IChmb3YudXBUYW4gLSBmb3YuZG93blRhbikgKiBweXNjYWxlICogMC41O1xuICAgIHJldHVybiB7IHNjYWxlOiBbIHB4c2NhbGUsIHB5c2NhbGUgXSwgb2Zmc2V0OiBbIHB4b2Zmc2V0LCBweW9mZnNldCBdIH07XG59XG5cbmZ1bmN0aW9uIGZvdlBvcnRUb1Byb2plY3Rpb24oIGZvdjogYW55LCByaWdodEhhbmRlZD86IGJvb2xlYW4sIHpOZWFyPyA6IG51bWJlciwgekZhcj8gOiBudW1iZXIgKSB7XG5cbiAgICByaWdodEhhbmRlZCA9IHJpZ2h0SGFuZGVkID09PSB1bmRlZmluZWQgPyB0cnVlIDogcmlnaHRIYW5kZWQ7XG4gICAgek5lYXIgPSB6TmVhciA9PT0gdW5kZWZpbmVkID8gMC4wMSA6IHpOZWFyO1xuICAgIHpGYXIgPSB6RmFyID09PSB1bmRlZmluZWQgPyAxMDAwMC4wIDogekZhcjtcblxuICAgIGxldCBoYW5kZWRuZXNzU2NhbGUgPSByaWdodEhhbmRlZCA/IC0xLjAgOiAxLjA7XG5cbiAgICAvLyBzdGFydCB3aXRoIGFuIGlkZW50aXR5IG1hdHJpeFxuICAgIGxldCBtb2JqID0gbmV3IFRIUkVFLk1hdHJpeDQoKTtcbiAgICBsZXQgbSA9IG1vYmouZWxlbWVudHM7XG5cbiAgICAvLyBhbmQgd2l0aCBzY2FsZS9vZmZzZXQgaW5mbyBmb3Igbm9ybWFsaXplZCBkZXZpY2UgY29vcmRzXG4gICAgbGV0IHNjYWxlQW5kT2Zmc2V0ID0gZm92VG9ORENTY2FsZU9mZnNldChmb3YpO1xuXG4gICAgLy8gWCByZXN1bHQsIG1hcCBjbGlwIGVkZ2VzIHRvIFstdywrd11cbiAgICBtWzAgKiA0ICsgMF0gPSBzY2FsZUFuZE9mZnNldC5zY2FsZVswXTtcbiAgICBtWzAgKiA0ICsgMV0gPSAwLjA7XG4gICAgbVswICogNCArIDJdID0gc2NhbGVBbmRPZmZzZXQub2Zmc2V0WzBdICogaGFuZGVkbmVzc1NjYWxlO1xuICAgIG1bMCAqIDQgKyAzXSA9IDAuMDtcblxuICAgIC8vIFkgcmVzdWx0LCBtYXAgY2xpcCBlZGdlcyB0byBbLXcsK3ddXG4gICAgLy8gWSBvZmZzZXQgaXMgbmVnYXRlZCBiZWNhdXNlIHRoaXMgcHJvaiBtYXRyaXggdHJhbnNmb3JtcyBmcm9tIHdvcmxkIGNvb3JkcyB3aXRoIFk9dXAsXG4gICAgLy8gYnV0IHRoZSBOREMgc2NhbGluZyBoYXMgWT1kb3duICh0aGFua3MgRDNEPylcbiAgICBtWzEgKiA0ICsgMF0gPSAwLjA7XG4gICAgbVsxICogNCArIDFdID0gc2NhbGVBbmRPZmZzZXQuc2NhbGVbMV07XG4gICAgbVsxICogNCArIDJdID0gLXNjYWxlQW5kT2Zmc2V0Lm9mZnNldFsxXSAqIGhhbmRlZG5lc3NTY2FsZTtcbiAgICBtWzEgKiA0ICsgM10gPSAwLjA7XG5cbiAgICAvLyBaIHJlc3VsdCAodXAgdG8gdGhlIGFwcClcbiAgICBtWzIgKiA0ICsgMF0gPSAwLjA7XG4gICAgbVsyICogNCArIDFdID0gMC4wO1xuICAgIG1bMiAqIDQgKyAyXSA9IHpGYXIgLyAoek5lYXIgLSB6RmFyKSAqIC1oYW5kZWRuZXNzU2NhbGU7XG4gICAgbVsyICogNCArIDNdID0gKHpGYXIgKiB6TmVhcikgLyAoek5lYXIgLSB6RmFyKTtcblxuICAgIC8vIFcgcmVzdWx0ICg9IFogaW4pXG4gICAgbVszICogNCArIDBdID0gMC4wO1xuICAgIG1bMyAqIDQgKyAxXSA9IDAuMDtcbiAgICBtWzMgKiA0ICsgMl0gPSBoYW5kZWRuZXNzU2NhbGU7XG4gICAgbVszICogNCArIDNdID0gMC4wO1xuXG4gICAgbW9iai50cmFuc3Bvc2UoKTtcblxuICAgIHJldHVybiBtb2JqO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gZm92VG9Qcm9qZWN0aW9uKCAgZm92OiBhbnksIHJpZ2h0SGFuZGVkPzogYm9vbGVhbiwgek5lYXI/IDogbnVtYmVyLCB6RmFyPyA6IG51bWJlciApIHtcbiAgICBsZXQgREVHMlJBRCA9IE1hdGguUEkgLyAxODAuMDtcblxuICAgIGxldCBmb3ZQb3J0ID0ge1xuICAgICAgICB1cFRhbjogTWF0aC50YW4oIGZvdi51cERlZ3JlZXMgKiBERUcyUkFEICksXG4gICAgICAgIGRvd25UYW46IE1hdGgudGFuKCBmb3YuZG93bkRlZ3JlZXMgKiBERUcyUkFEICksXG4gICAgICAgIGxlZnRUYW46IE1hdGgudGFuKCBmb3YubGVmdERlZ3JlZXMgKiBERUcyUkFEICksXG4gICAgICAgIHJpZ2h0VGFuOiBNYXRoLnRhbiggZm92LnJpZ2h0RGVncmVlcyAqIERFRzJSQUQgKVxuICAgIH07XG5cbiAgICByZXR1cm4gZm92UG9ydFRvUHJvamVjdGlvbiggZm92UG9ydCwgcmlnaHRIYW5kZWQsIHpOZWFyLCB6RmFyICk7XG59IiwiLy8gQGZsb3dcblxuLyoqXG4gKiBQcmludHMgYSB3YXJuaW5nIGluIHRoZSBjb25zb2xlIGlmIGl0IGV4aXN0cy5cbiAqIERpc2FibGUgb24gcHJvZHVjdGlvbiBlbnZpcm9ubWVudC5cbiAqXG4gKiBAcGFyYW0ge1N0cmluZ30gbWVzc2FnZSBUaGUgd2FybmluZyBtZXNzYWdlLlxuICogQHJldHVybnMge3ZvaWR9XG4gKi9cbmV4cG9ydCBjb25zdCB3YXJuaW5nID0gKG1lc3NhZ2U6IHN0cmluZyk6IHZvaWQgPT4ge1xuICAgIC8vd2FybmluZyBtZXNzYWdlIG9ubHkgaGFwcGVuIG9uIGRldmVsb3AgZW52aXJvbm1lbnRcbiAgICBpZiAocHJvY2Vzcy5lbnYuTk9ERV9FTlYgIT09ICdwcm9kdWN0aW9uJykge1xuICAgICAgICBpZiAodHlwZW9mIGNvbnNvbGUgIT09IFwidW5kZWZpbmVkXCIgJiYgdHlwZW9mIGNvbnNvbGUuZXJyb3IgPT09IFwiZnVuY3Rpb25cIikge1xuICAgICAgICAgICAgY29uc29sZS5lcnJvcihtZXNzYWdlKTtcbiAgICAgICAgfVxuXG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IobWVzc2FnZSk7XG4gICAgICAgIH0gY2F0Y2ggKGUpIHtcbiAgICAgICAgfVxuICAgIH1cbn07XG5cbmV4cG9ydCBjb25zdCBjcm9zc0RvbWFpbldhcm5pbmcgPSAoKTogSFRNTEVsZW1lbnQgPT4ge1xuICAgIGxldCBlbGVtZW50ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCggJ2RpdicgKTtcbiAgICBlbGVtZW50LmNsYXNzTmFtZSA9IFwidmpzLWNyb3NzLWRvbWFpbi11bnN1cHBvcnRcIjtcbiAgICBlbGVtZW50LmlubmVySFRNTCA9IFwiU29ycnksIFlvdXIgYnJvd3NlciBkb24ndCBzdXBwb3J0IGNyb3NzIGRvbWFpbi5cIjtcbiAgICByZXR1cm4gZWxlbWVudDtcbn07Il19
