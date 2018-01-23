import { Component, OnInit, Inject, ViewEncapsulation, ViewChild, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';
import { ProcessParameter, ProcessParameterType } from 'app/models/ProcessParameter';
import { ProcessService } from 'app/services/process.service';

declare var hljs: any;
@Component({
  selector: 'app-artefact-dialog',
  templateUrl: './artefact-dialog.component.html',
  styleUrls: ['./artefact-dialog.component.scss'],
})
export class ArtefactDialogComponent implements OnInit {

  public selectedFormat = 'markdown';
  public data: any = {};

  public editMode = true;

  constructor( @Inject(MAT_DIALOG_DATA) public parameter: ProcessParameter<'input' | 'output'>) {

  }

  @ViewChild('code')
  public codeComponent: ElementRef;

  public ngOnInit() {
  }

  public getTypeInfo(type: number): [string, string] {
    return [ProcessService.getTypeName(type), ProcessService.getTypeColor(type)];
  }


  public clickEditButton() {
    const el: HTMLElement = this.codeComponent.nativeElement;

    if (this.editMode) {
      el.className = '';
      el.innerHTML = '';

      const format = this.parameter.type === ProcessParameterType.COMPLEX
        ? this.selectedFormat
        : 'markdown';

      el.classList.add(format);

      const data = this.parameter.type === ProcessParameterType.BOUNDING_BOX
        ? `${this.data.tx}, ${this.data.ty}, ${this.data.bx}, ${this.data.by}`
        : this.data.value;


      el.appendChild(document.createTextNode(data));
    }

    setTimeout(() => { hljs.highlightBlock(el); }, 20);
    this.editMode = !this.editMode;
  }
}
