#include <HalconCpp.h>
#include <HalconCDefs.h>
#include <HProto.h>
#include <HWindow.h>
#include <stdio.h>
#include "MvCameraControl.h"
#include "PixelType.h"

/*���������붨��*/
typedef int Status;
#define STATUS_OK               0
#define STATUS_ERROR            -1


using namespace Halcon;

/** @fn     ConvertPixelTypeToMono8(IN OUT unsigned char *pInData, IN OUT unsigned char *pOutData,IN unsigned int nDataSize, 
                                    IN OUT MV_FRAME_OUT_INFO_EX* pFrameInfo,MvGvspPixelType enGvspPixelType)
 *  @brief  ת�����ظ�ʽΪMono8
 *  @param  pInData           [IN][OUT]   - �������ݻ���
 *  @param  pOutData           [IN][OUT]   - ��������ݻ���
 *  @param  nDataSize       [IN]        - �����С
 *  @param  pFrameInfo      [IN][OUT]   - �������֡��Ϣ
 *  
 *  @return �ɹ�������MV_OK��ʧ�ܣ����ش�����
 */
Status ConvertToMono8(void *pHandle, IN OUT unsigned char *pInData, IN OUT unsigned char *pOutData,IN int nHeight,IN int nWidth,
                            MvGvspPixelType nPixelType);

/************************************************************************
 *  @fn     ConvertToRGB()
 *  @brief  ת��ΪRGB��ʽ����
 *  @param  pHandle                [IN]           ���
 *  @param  pSrc                   [IN]           Դ����
 *  @param  nHeight                [IN]           ͼ��߶�
 *  @param  nWidth                 [IN]           ͼ����
 *  @param  enGvspPixelType        [IN]           Դ���ݸ�ʽ
 *  @param  pDst                   [OUT]          ת��������
 *  @return �ɹ�������STATUS_OK�����󣬷���STATUS_ERROR 
 ************************************************************************/
Status ConvertToRGB(void *pHandle, unsigned char *pSrc, int nHeight, int nWidth, MvGvspPixelType nPixelType, unsigned char *pDst);

/************************************************************************
 *  @fn     ConvertRGBToHalcon()
 *  @brief  ת��ΪRGB��ʽ����
 *  @param  pHandle                [IN]           ���
 *  @param  Hobj                   [OUT]          ת��������Hobject����
 *  @param  nHeight                [IN]           ͼ��߶�
 *  @param  nWidth                 [IN]           ͼ����
 *  @param  nPixelType             [IN]           Դ���ݸ�ʽ
 *  @param  pData                  [IN]           Դ����
 *  @return �ɹ�������STATUS_OK�����󣬷���STATUS_ERROR 
 ************************************************************************/
Status ConvertMono8ToHalcon(Halcon::Hobject *Hobj, int nHeight, int nWidth, MvGvspPixelType nPixelType, unsigned char *pData);

/************************************************************************
 *  @fn     ConvertRGBToHalcon()
 *  @brief  ת��ΪRGB��ʽ����
 *  @param  pHandle                [IN]           ���
 *  @param  Hobj                   [OUT]          ת��������Hobject����
 *  @param  nHeight                [IN]           ͼ��߶�
 *  @param  nWidth                 [IN]           ͼ����
 *  @param  nPixelType             [IN]           Դ���ݸ�ʽ
 *  @param  pData                  [IN]           Դ����
 *  @param  pData                  [IN]           �洢������ɫԴ���ݵĻ�����
 *  @return �ɹ�������STATUS_OK�����󣬷���STATUS_ERROR 
 ************************************************************************/
Status ConvertRGBToHalcon(Halcon::Hobject *Hobj, int nHeight, int nWidth,
                          MvGvspPixelType nPixelType, unsigned char *pData, unsigned char *pDataSeparate);

/************************************************************************
 *  @fn     IsColorPixelFormat()
 *  @brief  �ж��Ƿ��ǲ�ɫ��ʽ
 *  @param  enType                [IN]            ���ظ�ʽ
 *  @return ��ɫ������true���ڰף�����false 
 ************************************************************************/
bool IsColorPixelFormat(MvGvspPixelType enType);

/************************************************************************
 *  @fn     IsMonoPixelFormat()
 *  @brief  �ж��Ƿ��Ǻڰ׸�ʽ
 *  @param  enType                [IN]            ���ظ�ʽ
 *  @return �ڰף�����true����ɫ������false 
 ************************************************************************/
bool IsMonoPixelFormat(MvGvspPixelType enType);

/** @fn     HalconDisplay(HTuple *hWindow, const Halcon::Hobject &Hobj, HTuple hImageWidth, HTuple hImageHeight)
 *  @brief  Halconͼ����ʾ
 *  @param  hWindow               [IN]        - �������ݻ���
 *  @param  Hobj                  [IN]        - Halcon��ʽ����
 *  @return �ɹ�������STATUS_OK��
 */
Status HalconDisplay(HTuple *hWindow, const Halcon::Hobject &Hobj, const Halcon::HTuple &hImageWidth, const Halcon::HTuple &hImageHeight);
