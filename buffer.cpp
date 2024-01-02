/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 *
 * @details 哈工大数据库实验二，缓冲区管理器实现，来自Ashside，学号2021110908
 */

#include <memory>
#include <iostream>
#include "buffer.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"

/**
 * @brief Class for maintaining information about buffer pool frames
 */

namespace badgerdb
{
	/**
	 * @brief 构造函数
	 *
	 * @param bufs 缓冲池中的帧数
	 *
	 * @note
	 * 需要初始化缓冲池中的所有帧，即bufDescTable和bufPool。
	 * 需要初始化哈希表，即hashTable。
	 * 需要初始化clockHand，即指向缓冲池中的某一帧的指针。
	 */
	BufMgr::BufMgr(std::uint32_t bufs)
		: numBufs(bufs)
	{
		bufDescTable = new BufDesc[bufs];

		for (FrameId i = 0; i < bufs; i++)
		{
			bufDescTable[i].frameNo = i;
			bufDescTable[i].valid = false;
		}

		bufPool = new Page[bufs];

		int htsize = ((((int)(bufs * 1.2)) * 2) / 2) + 1;
		hashTable = new BufHashTbl(htsize); //< allocate the buffer hash table

		clockHand = bufs - 1;
	}

	/**
	 * @brief 析构函数
	 *
	 * @note
	 * 需要检查缓冲池中所有的dirty page，如果有，需要将其写回到磁盘。
	 * 之后，需要释放过程中所使用的所有内存。
	 * 即释放bufDescTable、bufPool、hashTable。
	 */
	BufMgr::~BufMgr()
	{
		for (FrameId i = 0; i < numBufs; i++)
		{
			/// @TODO: 是否必要检查valid标志位？
			/// @DONE: 确实没有必要
			if (bufDescTable[i].valid == true)
			{
				if (bufDescTable[i].dirty == true)
				{
					bufDescTable[i].file->writePage(bufPool[i]);
				}
			}
		}
		/// 释放内存
		delete[] bufDescTable;
		delete[] bufPool;
		delete hashTable;
	}

	/**
	 * @brief 顺时针旋转指针，指向下一个帧
	 */
	void BufMgr::advanceClock()
	{
		/// clokHand指向下一帧，需要取模以实现循环
		clockHand = (clockHand + 1) % numBufs;
	}

	/**
	 * @brief 使用时钟算法分配一个空闲的页框。
	 *
	 * @param frame 按引用传递，分配的页框号
	 *
	 * @note
	 * 如果页框是脏的，需要将其写回到磁盘。
	 * 如果缓冲池所有的页面都已经被固定，需要抛出BufferExceededException异常。
	 * 如果被分配的页框包含的页是有效的，需要在哈希表中删除该页。
	 *
	 */
	void BufMgr::allocBuf(FrameId &frame)
	{
		FrameId pinnedCnt = 0;
		/// 遍历缓冲池，找到一个空闲的页框
		/// 此处需要使用时钟算法
		while (1)
		{
			advanceClock();
			/// 如果找到空闲页框
			if (bufDescTable[clockHand].valid == false)
			{
				frame = clockHand;
				return;
			}

			/// 运行时钟算法
			if (bufDescTable[clockHand].refbit == true)
			{
				/// 如果找到的页框的refbit为true，将其置为false
				/// 继续寻找
				bufDescTable[clockHand].refbit = false;
				continue;
			}

			/// 如果找到固定的页框
			if (bufDescTable[clockHand].pinCnt > 0)
			{
				pinnedCnt++;
				/// 如果所有的页框都被固定
				if (pinnedCnt == numBufs)
				{
					throw BufferExceededException();
				}
				else
				{
					continue;
				}
			}

			/// 写回脏页
			if (bufDescTable[clockHand].dirty == true)
			{
				/// 调用file->writePage()方法将页框的内容写回到磁盘
				bufDescTable[clockHand].file->writePage(bufPool[clockHand]);
				/// 写回后，将dirty标志位置为false
				bufDescTable[clockHand].dirty = false;
			}
			/**
			 * 如果找到的页框包含的页是有效的
			 * 事实上，这里已经是流程图的最后一步，这个判断没有意义
			 * if (bufDescTable[clockHand].valid == true)
			*/

			/**
			 * 在哈希表中删除该页
			 * hashTable->remove(bufDescTable[clockHand].file, bufDescTable[clockHand].pageNo);
			 * try catch删除
			*/

			try
			{
				hashTable->remove(bufDescTable[clockHand].file, bufDescTable[clockHand].pageNo);
			}
			catch (HashNotFoundException e)
			{
				/// 会产生不知名报错
				/// std::cout << e.what() << std::endl;
			}
			frame = clockHand;
			return;
		}
	}

	/**
	 * @brief 寻找页框的指针
	 *
	 * @param file  	文件指针
	 * @param PageNo  	页号
	 * @param page  		页指针

	 * @note
	 * 首先调用lookup()方法检查是否在缓冲池中。
	 * 如果在，则通过page返回指向页框的指针。将页框的refbit设置为true，并将页框的pinCnt加一。
	 * 如果不在，则会捕捉到HashNotFoundException异常，调用allocBuf()方法分配一个空闲页框。
	 * 之后，需要通过file->readPage()将页框的内容从磁盘读取到缓冲池中。
	 * 再之后，在哈希表中插入该页，调用Set()方法设置页框的成员变量。
	 * 最后，通过page返回指向页框的指针。
	 *
	*/
	void BufMgr::readPage(File *file, const PageId pageNo, Page *&page)
	{
		/// 首先调用lookup()方法检查是否在缓冲池中。
		FrameId frameNo;
		try
		{
			/// 如果在,将页框的refbit设置为true，并将页框的pinCnt加一。
			hashTable->lookup(file, pageNo, frameNo);
			bufDescTable[frameNo].refbit = true;
			bufDescTable[frameNo].pinCnt++;
		}
		catch (HashNotFoundException e)
		{
			/// 如果不在，则会捕捉到HashNotFoundException异常，调用allocBuf()方法分配一个空闲页框。
			allocBuf(frameNo);
			/// 之后，需要通过file->readPage()将页框的内容从磁盘读取到缓冲池中。
			bufPool[frameNo] = file->readPage(pageNo);
			/// 再之后，在哈希表中插入该页，调用Set()方法设置页框的成员变量。
			hashTable->insert(file, pageNo, frameNo);
			bufDescTable[frameNo].Set(file, pageNo);
		}
		/// 最后，通过page返回指向页框的指针。
		page = &bufPool[frameNo];
	}

	/**
	 * @brief 将pinCnt减一
	 *
	 * @param file 	文件指针
	 * @param PageNo 	页号
	 * @param dirty 	是否脏页
	 *
	 * @note
	 * 如果参数dirty为true，则将页框的dirty标志位置为true。
	 * 如果pinCnt已经为0，则抛出PAGENOTPINNED异常。
	 * 如果不在哈希表中，则什么都不做
	 */
	void BufMgr::unPinPage(File *file, const PageId pageNo, const bool dirty)
	{
		FrameId frameNo;

		/// 从哈希表中查找
		try
		{
			hashTable->lookup(file, pageNo, frameNo);
		}
		catch (HashNotFoundException e)
		{
			/// 这里没有要求抛出异常
			/// 直接返回
			return;
		}

		if (bufDescTable[frameNo].pinCnt > 0)
		{
			/// 如果参数dirty为true，则将页框的dirty标志位置为true。
			bufDescTable[frameNo].pinCnt--;
			if (dirty == true)
			{
				bufDescTable[frameNo].dirty = true;
			}
		}
		else if (bufDescTable[frameNo].pinCnt == 0)
		{
			/// 如果pinCnt已经为0，则抛出PAGENOTPINNED异常。
			throw PageNotPinnedException(bufDescTable[frameNo].file->filename(), bufDescTable[frameNo].pageNo, frameNo);
		}
	}
	/**
	 * @brief 扫描bufTable，检索缓冲区中所有属于文件file的页，进行flush操作
	 *
	 * @param file 文件指针
	 *
	 * @note
	 * 如果页面是脏的，则将其写回到磁盘，置dirty标志位为false。
	 * 将页面从哈希表删除
	 * 调用BufDesc的Clear()方法，将页框的成员变量重置为初始值。
	 * 对于无效的页，抛出异常
	 * 对于固定的页，抛出异常
	 *
	 * @exception BadBufferException
	 */
	void BufMgr::flushFile(const File *file)
	{
		/// 遍历bufTable
		for (FrameId frameno = 0; frameno < numBufs; frameno++)
		{
			if (bufDescTable[frameno].file == file)
			{
				/// 对于无效的页，抛出异常
				if (bufDescTable[frameno].valid == false)
				{
					throw BadBufferException(frameno, bufDescTable[frameno].dirty, bufDescTable[frameno].valid, bufDescTable[frameno].refbit);
				}
				/// 对于固定的页，抛出异常
				if (bufDescTable[frameno].pinCnt > 0)
				{
					throw PagePinnedException(file->filename(), bufDescTable[frameno].pageNo, frameno);
				}
				/// 如果页面是脏的，则将其写回到磁盘，置dirty标志位为false。
				if (bufDescTable[frameno].dirty == true)
				{
					bufDescTable[frameno].file->writePage(bufPool[frameno]);
					bufDescTable[frameno].dirty = false;
				}
				/// 将页面从哈希表删除
				hashTable->remove(bufDescTable[frameno].file, bufDescTable[frameno].pageNo);
				/// 调用BufDesc的Clear()方法，将页框的成员变量重置为初始值。
				bufDescTable[frameno].Clear();
			}
		}
	}

	/**
	 * @brief 分配页框
	 *
	 * @param file 文件指针
	 * @param pageNo 返回新分配页面的页号
	 * @param page 返回新分配页面的页框的指针
	 *
	 * @note
	 * 首先调用file->allocatePage()方法在file文件中分配一个空闲页面，页指针为返回值
	 * 调用allocBuf()方法在缓冲区中分配一个空闲的页框
	 * 在哈希表中插入一条项目，并通过Set()方法设置状态
	 */
	void BufMgr::allocPage(File *file, PageId &pageNo, Page *&page)
	{
		/// 从文件中分配一个空闲页面
		auto newPage = file->allocatePage();

		/// 在缓冲区中分配一个空闲的页框
		FrameId frameNo;
		allocBuf(frameNo);

		/// 将页框的内容从磁盘读取到缓冲池中
		bufPool[frameNo] = newPage;

		/// 在哈希表中插入一条项目，并通过Set()方法设置状态
		hashTable->insert(file, newPage.page_number(), frameNo);
		bufDescTable[frameNo].Set(file, newPage.page_number());

		/// 通过page返回指向页框的指针
		page = &bufPool[frameNo];
		pageNo = newPage.page_number();
	}

	/**
	 * @brief 从file中删除页号为pageNo的页面
	 *
	 * @note
	 * 如果该页面在缓冲池中，需要清空所在的页框并从哈希表中删除
	 */
	void BufMgr::disposePage(File *file, const PageId PageNo)
	{
		FrameId frameno;
		/// 从哈希表中查找
		try
		{
			hashTable->lookup(file, PageNo, frameno);

			/// 如果该页面在缓冲池中，需要清空所在的页框并从哈希表中删除
			if (bufDescTable[frameno].valid == true)
			{
				hashTable->remove(file, PageNo);
				bufDescTable[frameno].Clear();
			}
		}
		catch (HashNotFoundException e)
		{
		}
		/// 从文件中删除页号为pageNo的页面
		file->deletePage(PageNo);
	}

	void BufMgr::printSelf(void)
	{
		BufDesc *tmpbuf;
		int validFrames = 0;

		for (std::uint32_t i = 0; i < numBufs; i++)
		{
			tmpbuf = &(bufDescTable[i]);
			std::cout << "FrameNo:" << i << " ";
			tmpbuf->Print();

			if (tmpbuf->valid == true)
				validFrames++;
		}

		std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
	}
}
