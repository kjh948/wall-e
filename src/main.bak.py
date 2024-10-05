from time import sleep
import multiprocessing as mp
import argparse

from sense import detect

processes = []
#sense
frameBuffer = None
detectRestults = None


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="./resources/model/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite", help="Path of the detection model.")
    parser.add_argument("--label", default="./resources/model/coco_labels.txt", help="Path of the labels file.")
    args = parser.parse_args()

    model    = args.model
    # label    = ReadLabelFile(args.label)

    
    camera_width = 320
    camera_height = 240

    try:
        mp.set_start_method('forkserver')
        frameBuffer = mp.Queue(10)
        detectRestults = mp.Queue()

        # Start streaming
        p = mp.Process(target=detect.detectThread,
                       args=(args, frameBuffer, detectRestults),
                       daemon=True)
        p.start()
        processes.append(p)

        # Activation of inferencer
        # devices = edgetpu_utils.ListEdgeTpuPaths(edgetpu_utils.EDGE_TPU_STATE_UNASSIGNED)
        # devices = [0]
        # for devnum in range(len(devices)):
        #     p = mp.Process(target=inferencer,
        #                    args=(results, frameBuffer, model, camera_width, camera_height),
        #                    daemon=True)
        #     p.start()
        #     processes.append(p)

        while True:
            sleep(1)

    finally:
        for p in range(len(processes)):
            processes[p].terminate()


