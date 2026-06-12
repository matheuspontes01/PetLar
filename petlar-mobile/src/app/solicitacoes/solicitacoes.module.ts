import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';

import { IonicModule } from '@ionic/angular';

import { SolicitacoesPage } from './solicitacoes.page';
import { SolicitacoesPageRoutingModule } from './solicitacoes-routing.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    SolicitacoesPageRoutingModule
  ],
  declarations: [SolicitacoesPage]
})
export class SolicitacoesPageModule {}
