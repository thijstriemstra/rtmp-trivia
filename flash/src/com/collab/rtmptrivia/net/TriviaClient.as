// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.net
{
	import com.collab.rtmptrivia.events.TriviaEvent;
	
	import flash.events.EventDispatcher;

	/**
	 * Trivia callback client. Dispatches <code>TriviaEvent</code>s to notify others
	 * of incoming messages.
	 * 
	 * @langversion 3.0
     * @playerversion Flash 9
	 */	
	public class TriviaClient extends EventDispatcher
	{
		private var _evt	: TriviaEvent;
		
		/**
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
		 * @param answer
		 */		
		public function showAnswer( answer:String ):void
		{
			_evt = new TriviaEvent( TriviaEvent.SHOW_ANSWER );
			_evt.answer = answer;
			dispatchEvent( _evt );
		}
		
		/**
		 * @param question
		 */		
		public function newQuestion( question:Object ):void
		{
			_evt = new TriviaEvent( TriviaEvent.NEW_QUESTION );
			_evt.question = question;
			dispatchEvent( _evt );
		}
		
	}
}