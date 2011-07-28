// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia
{
	/**
	 * RTMP callback client.
	 */	
	public class TestClient
	{
		/**
		 * @param hint
		 * @param index
		 */		
		public function newHint(hint:String, index:Number):void
		{
			trace('newHint: ' + index.toString() + " - " + hint);
		}
		
		/**
		 * @param answer
		 */		
		public function showAnswer(answer:String):void
		{
			trace('showAnswer: ' + answer);
		}
		
		/**
		 * @param question
		 */		
		public function newQuestion(question:Object):void
		{
			trace('newQuestion: ' + question.question);
		}
		
	}
}