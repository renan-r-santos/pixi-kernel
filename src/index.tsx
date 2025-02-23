import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { showErrorMessage } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import {
  IFormRenderer,
  IFormRendererRegistry
} from '@jupyterlab/ui-components';
import type { WidgetProps } from '@rjsf/utils';
import React from 'react';

import { PixiEnvWidget } from './env';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pixi-kernel:plugin',
  description: 'Jupyter kernels using Pixi for reproducible notebooks.',
  autoStart: true,
  requires: [IFormRendererRegistry, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    formRegistry: IFormRendererRegistry,
    nbTracker: INotebookTracker
  ) => {
    try {
      const component: IFormRenderer = {
        widgetRenderer: (props: WidgetProps) =>
          PixiEnvWidget({ ...props, app, nbTracker })
      };
      formRegistry.addRenderer('pixi-kernel:plugin.pixi-envs', component);
    } catch (error) {
      showErrorMessage('Pixi Kernel Error', {
        message: (
          <pre>{error instanceof Error ? error.message : String(error)}</pre>
        )
      });
    }
  }
};

export default plugin;
