// Leap_MotionC++.cpp : Defines the entry point for the console application.
//
/*
*	legend
*/


#include "stdafx.h"

#include <iostream>
#include <cstring>
#include <Windows.h>
#include "Leap.h"

#define SAMPLE_TIME_MS 20
#define INIT_TIME_MS 100
#define SIZE_BUFF 163
#define DEBUG_MODE

using namespace Leap;

Controller controller;
float buffer[SIZE_BUFF];

double current_timestamp;
float seq_number;
unsigned char *leap_buffer;
HANDLE timer_handle;


unsigned char *OpenSharedMemoryBuffer(char *name,int buf_size)
{

	//Apre un nmemory buffer. Se non esiste lo crea.
	HANDLE hMapFile;

	hMapFile = CreateFileMapping(
		INVALID_HANDLE_VALUE,    // use paging file
		NULL,                    // default security
		PAGE_READWRITE,          // read/write access
		0,                       // maximum object size (high-order DWORD)
		buf_size,                // maximum object size (low-order DWORD)
		name);                 // name of mapping object

	if (hMapFile == NULL)
		{
		printf("Could not create file mapping object.\n");
		return NULL;
		}

	return (unsigned char*)MapViewOfFile(hMapFile,   // handle to map object
		FILE_MAP_ALL_ACCESS, // read/write permission
		0,
		0,
		buf_size);

}

void init_buffer()
{
	for (int i=0; i< SIZE_BUFF; i++)
	{
		buffer[i] = 0;
	}
}

void read_frame() 
{
	float x = 0, z = 0, y = 0;
	int offset;

#ifdef DEBUG_MODE
	std::cout << "dentro il task" << std::endl;
#endif

	init_buffer();
	Frame f = controller.frame();

	/*
	*	Check if a new frame is arrived
	*/
	if (f.timestamp() < current_timestamp) return;

	current_timestamp = f.timestamp();
	buffer[0] = ++seq_number;

#ifdef DEBUG_MODE
	std::cout << "timestamp corrente: " << current_timestamp << " " << buffer[0] << std::endl;
#endif

	HandList hands;
    hands = f.hands();

	for (HandList::const_iterator hl = hands.begin(); hl != hands.end(); ++hl) {
		Hand hand = *hl;
		if (hand.isRight()) {
			offset = 0;
		} else {
			offset = 75 + 6;
		}
		// palm position
		buffer[offset + 1] = hand.palmPosition().x;
		buffer[offset + 2] = hand.palmPosition().y;
		buffer[offset + 3] = hand.palmPosition().z; 

		// palm normal
		buffer[offset + 4] = hand.palmNormal().x;
		buffer[offset + 5] = hand.palmNormal().y;
		buffer[offset + 6] = hand.palmNormal().z;

		// fingers
		FingerList fingers = hand.fingers();
		for(Leap::FingerList::const_iterator fl = fingers.begin(); fl != fingers.end(); fl++){
			// (*fl).type() identifies the finger [0 - 4] from thumb to pinky
			int off_finger = (*fl).type()*3*5 + offset + 6;
			
			Leap::Bone bone;
			Leap::Bone::Type boneType;
			/*
			* all bones: Metacarpal (0), Proximal (1), Intermediate (2), Distal(3)
			*/
			for(int b = 0; b < 4; b++) 
			{
				int off_finger_bone = off_finger + b*3;
				boneType = static_cast<Leap::Bone::Type>(b);
				bone = (*fl).bone(boneType);
				buffer[off_finger_bone + 1] = bone.prevJoint().x;
				buffer[off_finger_bone + 2] = bone.prevJoint().y;
				buffer[off_finger_bone + 3] = bone.prevJoint().z;
				
				if (b == 3)
				{
					buffer[off_finger_bone + 4] = bone.nextJoint().x;
					buffer[off_finger_bone + 5] = bone.nextJoint().y;
					buffer[off_finger_bone + 6] = bone.nextJoint().z;
				}
			}
		}

	}
#ifdef DEBUG_MODE
	for (int i=0; i < SIZE_BUFF; i++)
	{
		std::cout << buffer[i] << std::endl;
	}
#endif


	memcpy((void *)leap_buffer, (void *)buffer, (4*SIZE_BUFF));

}

void CALLBACK timer_function(void* /*lpParameter*/,BOOLEAN /*TimerOrWaitFired*/)
{
    /* what happens during periodic task */
	read_frame();
}


void start_timer(DWORD milliseconds_before_first_call, DWORD milliseconds_between_calls)
{

    //void* parameter; /* passed as lpParameter of timer_function */
    //DWORD milliseconds_before_first_call=100; /* execute after 100ms */
    //DWORD milliseconds_between_calls=500; /* and then every 500ms */
    CreateTimerQueueTimer(&timer_handle,NULL,timer_function,NULL,
        milliseconds_before_first_call,milliseconds_between_calls,
        WT_EXECUTELONGFUNCTION /* the function takes a while, and may block */
    );
}

int _tmain(int argc, _TCHAR* argv[])
{	
	controller.setPolicy(Leap::Controller::POLICY_BACKGROUND_FRAMES);
	leap_buffer = OpenSharedMemoryBuffer("LeapBuffer" , (4*SIZE_BUFF));
	//controller.setPolicy(Leap::Controller::POLICY_ALLOW_PAUSE_RESUME);

	/*
	*	Manage periodic task
	*/
	start_timer(INIT_TIME_MS,SAMPLE_TIME_MS);

	while (true) {
	}

	return 0;
}

