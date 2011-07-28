// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.net
{
	import com.collab.rtmptrivia.events.TriviaEvent;
	
	import flash.events.EventDispatcher;

	/**
	 * Trivia callback client. Dispatches <code>TriviaEvent</code>s to notify others
	 * of incoming events.
	 * 
	 * @langversion 3.0
     * @playerversion Flash 9
	 */	
	public class TriviaClient extends EventDispatcher
	{
		// ====================================================================
		// PRIVATE VARS
		// ====================================================================
		
		private var _evt	: TriviaEvent;
		
		/**
		 * Creates a new TriviaClient object. 
		 */		
		public function TriviaClient()
		{
			super();
		}
		
		// ====================================================================
		// PUBLIC CALLBACK METHODS
		// ====================================================================
		
		/**
		 * Invoked when the trivia game sends a new hint.
		 *  
		 * Dispatches a <code>TriviaEvent.NEW_HINT</code> event.
		 * 
		 * @param hint
		 * @param index
		 */		
		public function newHint( hint:String, index:Number ):void
		{
			_evt = new TriviaEvent( TriviaEvent.NEW_HINT );
			_evt.hintIndex = index;
			_evt.hint = hint;
			
			dispatchEvent( _evt );
		}
		
		/**
		 * Invoked when the answer wasn't guessed.
		 *  
		 * Dispatches a <code>TriviaEvent.SHOW_ANSWER</code> event.
		 * 
		 * @param answer
		 */		
		public function showAnswer( answer:String ):void
		{
			_evt = new TriviaEvent( TriviaEvent.SHOW_ANSWER );
			_evt.answer = answer;
			
			dispatchEvent( _evt );
		}
		
		/**
		 * Invoked when a new trivia question is received.
		 * 
		 * Dispatches a <code>TriviaEvent.NEW_QUESTION</code> event.
		 * 
		 * @param question
		 */		
		public function newQuestion( question:Object ):void
		{
			_evt = new TriviaEvent( TriviaEvent.NEW_QUESTION );
			_evt.question = question;
			
			dispatchEvent( _evt );
		}
		
		/**
		 * Invoked when a chat message is received.
		 * 
		 * Dispatches a <code>TriviaEvent.CHAT_MESSAGE</code> event.
		 * 
		 * @param message
		 * @param username
		 */		
		public function chatMessage( message:String, username:String ):void
		{
			_evt = new TriviaEvent( TriviaEvent.CHAT_MESSAGE );
			_evt.message = message;
			_evt.username = username;
			
			dispatchEvent( _evt );
		}
		
	}
}