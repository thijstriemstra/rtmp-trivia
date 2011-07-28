// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.net
{
	import com.collab.rtmptrivia.events.TriviaEvent;
	
	import flash.events.EventDispatcher;
	import flash.events.NetStatusEvent;
	import flash.events.SecurityErrorEvent;
	import flash.net.NetConnection;
	import flash.net.ObjectEncoding;
	
	/**
	 * @langversion 3.0
     * @playerversion Flash 9
	 */	
	public class TriviaConnection extends EventDispatcher
	{
		// ====================================================================
		// CONSTANTS
		// ====================================================================
		
		private const JOIN_SERVICE		: String = "playTrivia";
		private const ANSWER_SERVICE	: String = "giveAnswer";
		
		// ====================================================================
		// PRIVATE VARS
		// ====================================================================
		
		private var _url				: String;
		private var _username			: String;
		private var _nc					: NetConnection;
		private var _client				: Object;
		
		// ====================================================================
		// GETTER/SETTER
		// ====================================================================
		
		/**
		 * @return 
		 */		
		public function get connected():Boolean
		{
			var cn:Boolean = false;
			
			if ( _nc )
			{
				cn = _nc.connected;
			}
			
			return cn;
		}
		
		/**
		 * @return 
		 */		
		public function  get url():String
		{
			return _url;
		}
		
		/**
		 * @return 
		 */		
		public function  get username():String
		{
			return _username;
		}
		
		/**
		 * Creates a new TriviaConnection object.
		 */		
		public function TriviaConnection()
		{
			super();
		}
		
		// ====================================================================
		// PUBLIC METHODS
		// ====================================================================
		
		/**
		 * Connect to server.
		 * 
		 * @param url
		 * @param username
		 * @param client
		 */		
		public function connect( url:String, username:String, client:Object ):void
		{
			_url = url;
			_username = username;
			_client = client;
			
			if ( !_nc )
			{
				_nc = new NetConnection();
				// XXX: switch to AMF3 when rtmpy ticket #132 is resolved
				_nc.objectEncoding = ObjectEncoding.AMF0;
				_nc.addEventListener( NetStatusEvent.NET_STATUS, onStatus );
				_nc.addEventListener( SecurityErrorEvent.SECURITY_ERROR, onError );
			}
			
			if ( _username && _url && _client )
			{
				_nc.client = client;
				_nc.connect( _url, _username );
			}
		}
		
		/**
		 * Close server connection.
		 */		
		public function close():void
		{
			_nc.close();
		}
		
		/**
		 * Join the game.
		 */		
		public function join():void
		{
			_nc.call( JOIN_SERVICE, null, true );
		}
		
		/**
		 * Leave the game. 
		 */		
		public function leave():void
		{
			_nc.call( JOIN_SERVICE, null, false );
		}
		
		/**
		 * @param answer
		 */		
		public function answer( answer:String ):void
		{
			_nc.call( ANSWER_SERVICE, null, answer, _username, 0 );
		}
		
		// ====================================================================
		// EVENT HANDLERS
		// ====================================================================
		
		/**
		 * @param event
		 */		
		private function onStatus( event:NetStatusEvent ):void
		{
			event.stopImmediatePropagation();
			
			var evt:TriviaEvent;
			
			switch ( event.info.code )
			{
				case "NetConnection.Connect.Success":
					evt = new TriviaEvent( TriviaEvent.CONNECTION_SUCCESS );
					break;
				
				case "NetConnection.Connect.Closed":
					evt = new TriviaEvent( TriviaEvent.CONNECTION_CLOSED );
					break;
				
				case "NetConnection.Connect.Failed":
					evt = new TriviaEvent( TriviaEvent.CONNECTION_FAILED );
					break;
			}
			
			dispatchEvent( evt );
		}
		
		private function onError( event:SecurityErrorEvent ):void
		{
			event.stopImmediatePropagation();
		}
		
	}
}