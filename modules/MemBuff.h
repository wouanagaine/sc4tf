#ifndef __VirtualFileSystem_h_
#define __VirtualFileSystem_h_

#include <windows.h>

#include <string>

namespace VFS
{
	class MemoryBuffer
	{
		MemoryBuffer( const MemoryBuffer& );
		MemoryBuffer& operator=( const MemoryBuffer& );

	public:
		void* pBuffer;
		size_t nSize;
		MemoryBuffer()
			: pBuffer(0)
			, nSize(0)
		{
		}
		~MemoryBuffer()
		{
			delete[] pBuffer;
		}
		void Allocate( size_t nAllocSize )
		{
			delete[] pBuffer;
			pBuffer = new char[ nAllocSize ];
			nSize = nAllocSize;
		}
	};

	inline void ReadWhole( const std::wstring& strFile, MemoryBuffer& memBuff )
	{
		const std::wstring& strToOpen = strFile;
		HANDLE hHandle_ = ::CreateFile( strToOpen.c_str(), 
			GENERIC_READ,
			FILE_SHARE_READ,
			NULL,
			OPEN_EXISTING,
			FILE_ATTRIBUTE_NORMAL,
			NULL );

		int size = ::GetFileSize( hHandle_, NULL );
		memBuff.Allocate( size );
		unsigned long nRead = 0xFFFFFFFF;
		::ReadFile( hHandle_, memBuff.pBuffer, (unsigned int)size, &nRead, NULL );
		::CloseHandle( hHandle_ );

	}
}

#endif